from datetime import date, time
from functools import wraps
import json

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from horarios.disponibilidad import validar_espacio_libre

from .models import Cita


def _admin_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Inicia sesion para consultar las citas.'}, status=401)
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Esta consulta requiere permisos de administrador.'}, status=403)
        return view(request, *args, **kwargs)
    return wrapped


def _cita_json(cita):
    return {
        'id': cita.id,
        'paciente': cita.paciente,
        'medico': cita.medico,
        'fecha': cita.fecha.isoformat(),
        'hora': cita.hora.isoformat(),
        'estado': cita.estado,
        'estado_nombre': cita.get_estado_display(),
    }


@require_GET
@_admin_required
def consultar_citas(request):
    citas = Cita.objects.all()
    total_sistema = citas.count()

    fecha = request.GET.get('fecha', '').strip()
    if fecha:
        try:
            fecha_consulta = date.fromisoformat(fecha)
        except ValueError:
            return JsonResponse({'error': 'La fecha debe tener el formato AAAA-MM-DD.'}, status=400)
        citas = citas.filter(fecha=fecha_consulta)

    medico = request.GET.get('medico', '').strip()
    if medico:
        citas = citas.filter(medico__icontains=medico)

    estado = request.GET.get('estado', '').strip()
    if estado:
        estados_validos = {valor for valor, _ in Cita.ESTADOS}
        if estado not in estados_validos:
            return JsonResponse({'error': 'Selecciona un estado de cita valido.'}, status=400)
        citas = citas.filter(estado=estado)

    resultados = list(citas)
    return JsonResponse({
        'citas': [_cita_json(cita) for cita in resultados],
        'total': len(resultados),
        'total_sistema': total_sistema,
    })


TRANSICIONES_ESTADO = {
    Cita.ESTADO_PROGRAMADA: {Cita.ESTADO_CONFIRMADA, Cita.ESTADO_CANCELADA},
    Cita.ESTADO_CONFIRMADA: {Cita.ESTADO_COMPLETADA, Cita.ESTADO_CANCELADA},
    Cita.ESTADO_COMPLETADA: set(),
    Cita.ESTADO_CANCELADA: set(),
}


@require_POST
@_admin_required
def cambiar_estado_cita(request, cita_id):
    try:
        datos = json.loads(request.body or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'El cuerpo de la solicitud no contiene JSON válido.'}, status=400)

    nuevo_estado = datos.get('estado') if isinstance(datos, dict) else None
    estados_validos = {valor for valor, _ in Cita.ESTADOS}
    if nuevo_estado not in estados_validos:
        return JsonResponse({'error': 'Selecciona un estado de cita válido.'}, status=400)

    try:
        cita = Cita.objects.get(pk=cita_id)
    except Cita.DoesNotExist:
        return JsonResponse({'error': 'No se encontró la cita solicitada.'}, status=404)

    if nuevo_estado not in TRANSICIONES_ESTADO[cita.estado]:
        return JsonResponse({
            'error': f'No se permite cambiar una cita de {cita.get_estado_display()} a {dict(Cita.ESTADOS)[nuevo_estado]}.',
        }, status=409)

    cita.estado = nuevo_estado
    cita.save(update_fields=['estado'])
    return JsonResponse({'cita': _cita_json(cita), 'mensaje': 'El estado de la cita se actualizó correctamente.'})


@require_http_methods(['PATCH'])
@_admin_required
def gestionar_cita(request, cita_id):
    try:
        datos = json.loads(request.body or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'El cuerpo de la solicitud no contiene JSON válido.'}, status=400)
    if not isinstance(datos, dict):
        return JsonResponse({'error': 'Envía un objeto JSON válido.'}, status=400)

    try:
        with transaction.atomic():
            try:
                cita = Cita.objects.select_for_update().get(pk=cita_id)
            except Cita.DoesNotExist:
                return JsonResponse({'error': 'No se encontró la cita solicitada.'}, status=404)

            accion = datos.get('accion')
            if accion == 'cancelar':
                if set(datos) != {'accion'}:
                    return JsonResponse({'error': 'Para cancelar, envía únicamente la acción cancelar.'}, status=400)
                if cita.estado not in {Cita.ESTADO_PROGRAMADA, Cita.ESTADO_CONFIRMADA}:
                    return JsonResponse({'error': 'Solo se pueden cancelar citas programadas o confirmadas.'}, status=409)
                cita.estado = Cita.ESTADO_CANCELADA
                cita.save(update_fields=['estado'])
                mensaje = 'La cita fue cancelada y su horario quedó disponible.'
            else:
                if set(datos) != {'fecha', 'hora'}:
                    return JsonResponse({'error': 'Para reprogramar, envía una fecha y una hora.'}, status=400)
                if cita.estado not in {Cita.ESTADO_PROGRAMADA, Cita.ESTADO_CONFIRMADA}:
                    return JsonResponse({'error': 'Solo se pueden reprogramar citas programadas o confirmadas.'}, status=409)
                if not isinstance(datos['fecha'], str) or not isinstance(datos['hora'], str):
                    return JsonResponse({'error': 'La fecha y la hora deben ser texto válido.'}, status=400)
                try:
                    nueva_fecha = date.fromisoformat(datos['fecha'])
                    nueva_hora = time.fromisoformat(datos['hora'])
                except ValueError:
                    return JsonResponse({'error': 'Indica la fecha como AAAA-MM-DD y la hora como HH:MM.'}, status=400)
                if nueva_hora.second or nueva_hora.microsecond:
                    return JsonResponse({'error': 'La hora debe usar minutos exactos.'}, status=400)
                if nueva_fecha == cita.fecha and nueva_hora == cita.hora:
                    return JsonResponse({'cita': _cita_json(cita), 'mensaje': 'La cita conserva su fecha y hora actuales.'})

                _, error = validar_espacio_libre(
                    cita.medico,
                    nueva_fecha,
                    nueva_hora.strftime('%H:%M'),
                    excluir_cita_id=cita.id,
                    bloquear=True,
                )
                if error:
                    return JsonResponse({'error': error}, status=409)
                cita.fecha = nueva_fecha
                cita.hora = nueva_hora
                cita.save(update_fields=['fecha', 'hora'])
                mensaje = 'La cita se reprogramó correctamente.'

    except (TypeError, KeyError):
        return JsonResponse({'error': 'Los datos enviados no son válidos.'}, status=400)
    return JsonResponse({'cita': _cita_json(cita), 'mensaje': mensaje})
