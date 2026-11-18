import json
from functools import wraps

from django.db import IntegrityError
from django.db.models import Max
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from hospitales.models import Hospital
from .models import HospitalServicio, Servicio


def _admin_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Inicia sesion para continuar.'}, status=401)
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Esta accion requiere permisos de superusuario.'}, status=403)
        return view(request, *args, **kwargs)
    return wrapped


def _json_body(request):
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _servicio_json(servicio):
    return {
        'id': servicio.id,
        'numero': servicio.numero,
        'nombre': servicio.nombre,
        'descripcion': servicio.descripcion,
    }


def _asignacion_json(asignacion):
    return {
        'id': asignacion.id,
        'hospital_id': asignacion.hospital_id,
        'hospital_nombre': asignacion.hospital.nombre,
        'servicio_id': asignacion.servicio_id,
        'servicio_numero': asignacion.servicio.numero,
        'servicio_nombre': asignacion.servicio.nombre,
        'descripcion': asignacion.servicio.descripcion,
    }


def _validar_servicio(datos, actual=None):
    nombre = datos.get('nombre')
    descripcion = datos.get('descripcion', '')
    if not isinstance(nombre, str) or not nombre.strip():
        return None, 'Ingresa el nombre del servicio medico.'
    nombre = nombre.strip()
    if len(nombre) > 150:
        return None, 'El nombre admite hasta 150 caracteres.'
    if not isinstance(descripcion, str) or len(descripcion) > 1000:
        return None, 'La descripcion admite hasta 1000 caracteres.'
    repetidos = Servicio.objects.filter(nombre__iexact=nombre)
    if actual is not None:
        repetidos = repetidos.exclude(pk=actual.pk)
    if repetidos.exists():
        return None, 'Ya existe un servicio con ese nombre.'
    return {'nombre': nombre, 'descripcion': descripcion.strip()}, None


@require_http_methods(['GET', 'POST'])
@_admin_required
def administrar_servicios(request):
    if request.method == 'GET':
        servicios = Servicio.objects.all()
        return JsonResponse({'servicios': [_servicio_json(servicio) for servicio in servicios]})
    datos = _json_body(request)
    if datos is None:
        return JsonResponse({'error': 'Envia los datos en formato JSON valido.'}, status=400)
    valores, error = _validar_servicio(datos)
    if error:
        return JsonResponse({'error': error}, status=409 if error.startswith('Ya existe') else 400)
    numero = (Servicio.objects.aggregate(max_numero=Max('numero'))['max_numero'] or 0) + 1
    try:
        servicio = Servicio.objects.create(numero=numero, **valores)
    except IntegrityError:
        return JsonResponse({'error': 'Ya existe un servicio con ese nombre.'}, status=409)
    return JsonResponse({'servicio': _servicio_json(servicio)}, status=201)


@require_http_methods(['GET', 'PATCH'])
@_admin_required
def administrar_servicio(request, servicio_id):
    try:
        servicio = Servicio.objects.get(pk=servicio_id)
    except Servicio.DoesNotExist:
        return JsonResponse({'error': 'No se encontro ese servicio medico.'}, status=404)
    if request.method == 'GET':
        return JsonResponse({'servicio': _servicio_json(servicio)})
    datos = _json_body(request)
    if datos is None:
        return JsonResponse({'error': 'Envia los datos en formato JSON valido.'}, status=400)
    valores, error = _validar_servicio(datos, actual=servicio)
    if error:
        return JsonResponse({'error': error}, status=409 if error.startswith('Ya existe') else 400)
    servicio.nombre = valores['nombre']
    servicio.descripcion = valores['descripcion']
    try:
        servicio.save(update_fields=['nombre', 'descripcion'])
    except IntegrityError:
        return JsonResponse({'error': 'Ya existe un servicio con ese nombre.'}, status=409)
    return JsonResponse({'servicio': _servicio_json(servicio)})


@require_http_methods(['GET', 'POST'])
@_admin_required
def administrar_asignaciones(request):
    if request.method == 'GET':
        asignaciones = HospitalServicio.objects.select_related('hospital', 'servicio').all()
        return JsonResponse({'asignaciones': [_asignacion_json(item) for item in asignaciones]})
    datos = _json_body(request)
    if datos is None:
        return JsonResponse({'error': 'Envia los datos en formato JSON valido.'}, status=400)
    hospital_id = datos.get('hospital_id')
    servicio_id = datos.get('servicio_id')
    if any(isinstance(value, bool) or not str(value or '').isdigit() for value in (hospital_id, servicio_id)):
        return JsonResponse({'error': 'Selecciona un hospital y un servicio validos.'}, status=400)
    try:
        hospital = Hospital.objects.get(pk=int(hospital_id))
        servicio = Servicio.objects.get(pk=int(servicio_id))
    except (Hospital.DoesNotExist, Servicio.DoesNotExist):
        return JsonResponse({'error': 'El hospital o el servicio seleccionado no existe.'}, status=404)
    if HospitalServicio.objects.filter(hospital=hospital, servicio=servicio).exists():
        return JsonResponse({'error': 'Ese servicio ya esta asignado a este hospital.'}, status=409)
    try:
        asignacion = HospitalServicio.objects.create(hospital=hospital, servicio=servicio)
    except IntegrityError:
        return JsonResponse({'error': 'Ese servicio ya esta asignado a este hospital.'}, status=409)
    return JsonResponse({'asignacion': _asignacion_json(asignacion)}, status=201)