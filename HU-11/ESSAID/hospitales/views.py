import json
from functools import wraps

from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Hospital, ServicioMedico


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


@require_http_methods(['GET', 'POST'])
@_admin_required
def administrar_hospitales(request):
    if request.method == 'GET':
        return JsonResponse({'hospitales': [
            {'id': hospital.id, 'nombre': hospital.nombre,
             'direccion': hospital.direccion, 'contacto': hospital.contacto}
            for hospital in Hospital.objects.all()
        ]})

    datos = _json_body(request)
    if datos is None:
        return JsonResponse({'error': 'Envia los datos en formato JSON valido.'}, status=400)

    valores = [datos.get(campo) for campo in ('nombre', 'direccion', 'contacto')]
    if any(not isinstance(valor, str) or not valor.strip() for valor in valores):
        return JsonResponse({'error': 'Completa el nombre, la direccion y el contacto.'}, status=400)
    nombre, direccion, contacto = (valor.strip() for valor in valores)
    if len(nombre) > 150 or len(direccion) > 255 or len(contacto) > 100:
        return JsonResponse({'error': 'El nombre admite 150 caracteres, la direccion 255 y el contacto 100.'}, status=400)
    if Hospital.objects.filter(nombre__iexact=nombre).exists():
        return JsonResponse({'error': 'Ya existe un hospital con ese nombre.'}, status=409)

    try:
        hospital = Hospital.objects.create(nombre=nombre, direccion=direccion, contacto=contacto)
    except IntegrityError:
        return JsonResponse({'error': 'Ya existe un hospital con ese nombre.'}, status=409)
    return JsonResponse({'hospital': {
        'id': hospital.id, 'nombre': hospital.nombre,
        'direccion': hospital.direccion, 'contacto': hospital.contacto,
    }}, status=201)

def _hospital_json(hospital):
    return {
        'id': hospital.id,
        'nombre': hospital.nombre,
        'direccion': hospital.direccion,
        'contacto': hospital.contacto,
    }


@require_http_methods(['GET', 'PATCH'])
@_admin_required
def administrar_hospital(request, hospital_id):
    try:
        hospital = Hospital.objects.get(pk=hospital_id)
    except Hospital.DoesNotExist:
        return JsonResponse({'error': 'No se encontro ese hospital.'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'hospital': _hospital_json(hospital)})

    datos = _json_body(request)
    if datos is None:
        return JsonResponse({'error': 'Envia los datos en formato JSON valido.'}, status=400)

    valores = [datos.get(campo) for campo in ('nombre', 'direccion', 'contacto')]
    if any(not isinstance(valor, str) or not valor.strip() for valor in valores):
        return JsonResponse({'error': 'Completa el nombre, la direccion y el contacto.'}, status=400)
    nombre, direccion, contacto = (valor.strip() for valor in valores)
    if len(nombre) > 150 or len(direccion) > 255 or len(contacto) > 100:
        return JsonResponse({'error': 'El nombre admite 150 caracteres, la direccion 255 y el contacto 100.'}, status=400)
    if Hospital.objects.filter(nombre__iexact=nombre).exclude(pk=hospital.pk).exists():
        return JsonResponse({'error': 'Ya existe otro hospital con ese nombre.'}, status=409)

    hospital.nombre = nombre
    hospital.direccion = direccion
    hospital.contacto = contacto
    try:
        hospital.save(update_fields=['nombre', 'direccion', 'contacto'])
    except IntegrityError:
        return JsonResponse({'error': 'Ya existe otro hospital con ese nombre.'}, status=409)
    return JsonResponse({'hospital': _hospital_json(hospital)})

def _servicio_json(servicio):
    return {
        'id': servicio.id,
        'hospital_id': servicio.hospital_id,
        'hospital_nombre': servicio.hospital.nombre,
        'nombre': servicio.nombre,
        'descripcion': servicio.descripcion,
    }


def _validar_servicio(datos, actual=None):
    nombre = datos.get('nombre')
    descripcion = datos.get('descripcion', '')
    hospital_id = datos.get('hospital_id')
    if not isinstance(nombre, str) or not nombre.strip():
        return None, 'Ingresa el nombre del servicio medico.'
    nombre = nombre.strip()
    if len(nombre) > 150:
        return None, 'El nombre admite hasta 150 caracteres.'
    if not isinstance(descripcion, str) or len(descripcion) > 1000:
        return None, 'La descripcion admite hasta 1000 caracteres.'
    if isinstance(hospital_id, bool) or not str(hospital_id or '').isdigit():
        return None, 'Selecciona un hospital valido.'
    try:
        hospital = Hospital.objects.get(pk=int(hospital_id))
    except Hospital.DoesNotExist:
        return None, 'Selecciona un hospital valido.'

    repetidos = ServicioMedico.objects.filter(hospital=hospital, nombre__iexact=nombre)
    if actual is not None:
        repetidos = repetidos.exclude(pk=actual.pk)
    if repetidos.exists():
        return None, 'Ese servicio ya esta registrado en el hospital seleccionado.'
    return {
        'hospital': hospital,
        'nombre': nombre,
        'descripcion': descripcion.strip(),
    }, None


@require_http_methods(['GET', 'POST'])
@_admin_required
def administrar_servicios(request):
    if request.method == 'GET':
        servicios = ServicioMedico.objects.select_related('hospital').all()
        hospital_id = request.GET.get('hospital_id')
        if hospital_id:
            if not hospital_id.isdigit():
                return JsonResponse({'error': 'El hospital seleccionado no es valido.'}, status=400)
            servicios = servicios.filter(hospital_id=int(hospital_id))
        return JsonResponse({'servicios': [_servicio_json(servicio) for servicio in servicios]})

    datos = _json_body(request)
    if datos is None:
        return JsonResponse({'error': 'Envia los datos en formato JSON valido.'}, status=400)
    valores, error = _validar_servicio(datos)
    if error:
        return JsonResponse({'error': error}, status=400 if 'ya esta registrado' not in error else 409)
    try:
        servicio = ServicioMedico.objects.create(**valores)
    except IntegrityError:
        return JsonResponse({'error': 'Ese servicio ya esta registrado en el hospital seleccionado.'}, status=409)
    return JsonResponse({'servicio': _servicio_json(servicio)}, status=201)


@require_http_methods(['GET', 'PATCH'])
@_admin_required
def administrar_servicio(request, servicio_id):
    try:
        servicio = ServicioMedico.objects.select_related('hospital').get(pk=servicio_id)
    except ServicioMedico.DoesNotExist:
        return JsonResponse({'error': 'No se encontro ese servicio medico.'}, status=404)
    if request.method == 'GET':
        return JsonResponse({'servicio': _servicio_json(servicio)})

    datos = _json_body(request)
    if datos is None:
        return JsonResponse({'error': 'Envia los datos en formato JSON valido.'}, status=400)
    valores, error = _validar_servicio(datos, actual=servicio)
    if error:
        return JsonResponse({'error': error}, status=400 if 'ya esta registrado' not in error else 409)
    servicio.hospital = valores['hospital']
    servicio.nombre = valores['nombre']
    servicio.descripcion = valores['descripcion']
    try:
        servicio.save(update_fields=['hospital', 'nombre', 'descripcion'])
    except IntegrityError:
        return JsonResponse({'error': 'Ese servicio ya esta registrado en el hospital seleccionado.'}, status=409)
    return JsonResponse({'servicio': _servicio_json(servicio)})