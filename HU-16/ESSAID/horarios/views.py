import json
from datetime import date, datetime, time, timedelta
from functools import wraps

from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from citas.models import Cita
from .disponibilidad import normalizar_nombre_medico
from usuarios.models import Medico

from .models import HorarioMedico


def _admin_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Inicia sesión para administrar horarios.'}, status=401)
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Esta acción requiere permisos de superusuario.'}, status=403)
        return view(request, *args, **kwargs)
    return wrapped


def _json_body(request):
    try:
        data = json.loads(request.body or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _nombre_medico(medico):
    return f'{medico.usuario.nombre} {medico.usuario.apellido}'.strip()


def _slots(horario):
    nombre = _nombre_medico(horario.medico)
    ocupadas = [
        cita.hora for cita in Cita.objects.filter(fecha=horario.fecha).exclude(estado=Cita.ESTADO_CANCELADA)
        if normalizar_nombre_medico(cita.medico) == normalizar_nombre_medico(nombre)
    ]
    inicio = datetime.combine(horario.fecha, horario.hora_inicio)
    fin = datetime.combine(horario.fecha, horario.hora_fin)
    paso = timedelta(minutes=horario.intervalo_minutos)
    ahora = timezone.localtime().replace(tzinfo=None, second=0, microsecond=0)
    resultado = []
    actual = inicio
    while actual + paso <= fin:
        hora = actual.time()
        siguiente = actual + paso
        ocupado = any(hora <= cita_hora < siguiente.time() for cita_hora in ocupadas)
        pasado = actual <= ahora
        resultado.append({
            'hora': hora.strftime('%H:%M'),
            'disponible': not ocupado and not pasado,
            'ocupado': ocupado,
        })
        actual = siguiente
    return resultado


def _horario_json(horario):
    slots = _slots(horario)
    return {
        'id': horario.id,
        'medico_id': horario.medico_id,
        'medico': _nombre_medico(horario.medico),
        'especialidad': horario.medico.especialidad,
        'fecha': horario.fecha.isoformat(),
        'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
        'hora_fin': horario.hora_fin.strftime('%H:%M'),
        'intervalo_minutos': horario.intervalo_minutos,
        'activo': horario.activo,
        'slots': slots,
        'total_disponibles': sum(slot['disponible'] for slot in slots),
        'total_ocupados': sum(slot['ocupado'] for slot in slots),
    }


def _validar_datos(datos, actual=None):
    campos = {'medico_id', 'fecha', 'hora_inicio', 'hora_fin', 'intervalo_minutos', 'activo'}
    desconocidos = set(datos) - campos
    if desconocidos:
        return None, 'La solicitud contiene campos no reconocidos.'

    medico_id = datos.get('medico_id', actual.medico_id if actual else None)
    if type(medico_id) is not int:
        return None, 'Selecciona un médico válido.'
    try:
        medico = Medico.objects.select_related('usuario').get(pk=medico_id)
    except Medico.DoesNotExist:
        return None, 'No se encontró el médico seleccionado.'

    try:
        fecha = date.fromisoformat(datos.get('fecha', actual.fecha.isoformat() if actual else ''))
    except (TypeError, ValueError):
        return None, 'Ingresa una fecha válida.'
    if fecha < timezone.localdate():
        return None, 'No se pueden registrar horarios en fechas pasadas.'

    try:
        inicio = time.fromisoformat(datos.get('hora_inicio', actual.hora_inicio.strftime('%H:%M') if actual else ''))
        fin = time.fromisoformat(datos.get('hora_fin', actual.hora_fin.strftime('%H:%M') if actual else ''))
    except (TypeError, ValueError):
        return None, 'Ingresa horas válidas.'
    if inicio.second or inicio.microsecond or fin.second or fin.microsecond or inicio >= fin:
        return None, 'La hora final debe ser posterior a la inicial y ambas deben usar minutos exactos.'

    intervalo = datos.get('intervalo_minutos', actual.intervalo_minutos if actual else 30)
    if type(intervalo) is not int or not 5 <= intervalo <= 240:
        return None, 'El intervalo debe ser un número entre 5 y 240 minutos.'
    duracion = (fin.hour * 60 + fin.minute) - (inicio.hour * 60 + inicio.minute)
    if duracion % intervalo:
        return None, 'El intervalo debe dividir exactamente el horario disponible.'

    activo = datos.get('activo', actual.activo if actual else True)
    if type(activo) is not bool:
        return None, 'El estado activo debe ser verdadero o falso.'

    return {
        'medico': medico,
        'fecha': fecha,
        'hora_inicio': inicio,
        'hora_fin': fin,
        'intervalo_minutos': intervalo,
        'activo': activo,
    }, None


def _hay_solapamiento(datos, actual=None):
    horarios = HorarioMedico.objects.filter(
        medico=datos['medico'],
        fecha=datos['fecha'],
        activo=True,
        hora_inicio__lt=datos['hora_fin'],
        hora_fin__gt=datos['hora_inicio'],
    )
    if actual is not None:
        horarios = horarios.exclude(pk=actual.pk)
    return horarios.exists()


@require_http_methods(['GET', 'POST'])
@_admin_required
def administrar_horarios(request):
    if request.method == 'GET':
        horarios = HorarioMedico.objects.select_related('medico__usuario').all()
        fecha_filtro = request.GET.get('fecha', '').strip()
        medico_filtro = request.GET.get('medico_id', '').strip()
        if fecha_filtro:
            try:
                horarios = horarios.filter(fecha=date.fromisoformat(fecha_filtro))
            except ValueError:
                return JsonResponse({'error': 'La fecha debe tener formato AAAA-MM-DD.'}, status=400)
        if medico_filtro:
            if not medico_filtro.isdecimal():
                return JsonResponse({'error': 'Selecciona un médico válido.'}, status=400)
            horarios = horarios.filter(medico_id=int(medico_filtro))
        medicos = Medico.objects.select_related('usuario').order_by('usuario__apellido', 'usuario__nombre')
        return JsonResponse({
            'horarios': [_horario_json(horario) for horario in horarios],
            'medicos': [{
                'id': medico.id,
                'nombre': _nombre_medico(medico),
                'especialidad': medico.especialidad,
            } for medico in medicos],
        })

    datos = _json_body(request)
    if datos is None:
        return JsonResponse({'error': 'Envía un objeto JSON válido.'}, status=400)
    valores, error = _validar_datos(datos)
    if error:
        return JsonResponse({'error': error}, status=400)
    try:
        with transaction.atomic():
            Medico.objects.select_for_update().get(pk=valores['medico'].pk)
            if valores['activo'] and _hay_solapamiento(valores):
                return JsonResponse({'error': 'El horario se cruza con otro horario activo de ese médico.'}, status=409)
            horario = HorarioMedico.objects.create(**valores)
    except IntegrityError:
        return JsonResponse({'error': 'Ese horario ya está registrado para el médico.'}, status=409)
    return JsonResponse({'horario': _horario_json(horario)}, status=201)


@require_http_methods(['PATCH'])
@_admin_required
def editar_horario(request, horario_id):
    try:
        horario = HorarioMedico.objects.select_related('medico__usuario').get(pk=horario_id)
    except HorarioMedico.DoesNotExist:
        return JsonResponse({'error': 'No se encontró el horario solicitado.'}, status=404)
    datos = _json_body(request)
    if datos is None:
        return JsonResponse({'error': 'Envía un objeto JSON válido.'}, status=400)
    valores, error = _validar_datos(datos, actual=horario)
    if error:
        return JsonResponse({'error': error}, status=400)
    try:
        with transaction.atomic():
            Medico.objects.select_for_update().get(pk=valores['medico'].pk)
            if valores['activo'] and _hay_solapamiento(valores, actual=horario):
                return JsonResponse({'error': 'El horario se cruza con otro horario activo de ese médico.'}, status=409)
            for campo, valor in valores.items():
                setattr(horario, campo, valor)
            horario.save()
    except IntegrityError:
        return JsonResponse({'error': 'Ese horario ya está registrado para el médico.'}, status=409)
    return JsonResponse({'horario': _horario_json(horario)})


@require_http_methods(['GET'])
def consultar_disponibilidad(request):
    fecha_valor = request.GET.get('fecha', '').strip()
    try:
        fecha = date.fromisoformat(fecha_valor)
    except ValueError:
        return JsonResponse({'error': 'Indica una fecha válida con formato AAAA-MM-DD.'}, status=400)
    if fecha < timezone.localdate():
        return JsonResponse({'error': 'La fecha consultada no puede estar en el pasado.'}, status=400)
    medico_valor = request.GET.get('medico_id', '').strip()
    horarios = HorarioMedico.objects.filter(activo=True, fecha=fecha).select_related('medico__usuario')
    if medico_valor:
        if not medico_valor.isdecimal():
            return JsonResponse({'error': 'El identificador del médico no es válido.'}, status=400)
        horarios = horarios.filter(medico_id=int(medico_valor))

    disponibles = []
    for horario in horarios:
        for slot in _slots(horario):
            if slot['disponible']:
                disponibles.append({
                    'horario_id': horario.id,
                    'medico_id': horario.medico_id,
                    'medico': _nombre_medico(horario.medico),
                    'especialidad': horario.medico.especialidad,
                    'fecha': fecha.isoformat(),
                    'hora': slot['hora'],
                })
    return JsonResponse({'fecha': fecha.isoformat(), 'horarios': disponibles, 'total': len(disponibles)})
