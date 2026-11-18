import json
from functools import wraps

from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Hospital


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


def _hospital_json(hospital):
    return {
        'id': hospital.id,
        'nombre': hospital.nombre,
        'direccion': hospital.direccion,
        'contacto': hospital.contacto,
        'activo': hospital.activo,
    }


@require_http_methods(['GET', 'POST'])
@_admin_required
def administrar_hospitales(request):
    if request.method == 'GET':
        return JsonResponse({'hospitales': [_hospital_json(hospital) for hospital in Hospital.objects.all()]})
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
    return JsonResponse({'hospital': _hospital_json(hospital)}, status=201)


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
    if set(datos) == {'activo'}:
        if not isinstance(datos['activo'], bool):
            return JsonResponse({'error': 'El estado activo debe ser verdadero o falso.'}, status=400)
        hospital.activo = datos['activo']
        hospital.save(update_fields=['activo'])
        return JsonResponse({'hospital': _hospital_json(hospital)})
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
