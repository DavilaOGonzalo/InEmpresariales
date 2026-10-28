import json
import re
from functools import wraps

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Medico, Paciente, Usuario


PERMISOS_POR_ROL = {
    'medico': {'paciente.leer', 'paciente.editar', 'medico.leer_propio', 'medico.editar_propio'},
    'paciente': {'paciente.leer_propio', 'paciente.editar_propio', 'medico.leer'},
}


def _validar_permisos(rol, permisos):
    if not isinstance(permisos, list) or any(not isinstance(p, str) for p in permisos):
        return 'Selecciona permisos validos.'
    if len(permisos) != len(set(permisos)) or not set(permisos).issubset(PERMISOS_POR_ROL.get(rol, set())):
        return 'Los permisos seleccionados no corresponden al rol.'
    return None


def _json_body(request):
    try:
        datos = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return datos if isinstance(datos, dict) else None


def _error_json():
    return JsonResponse({'error': 'Envía los datos en formato JSON válido.'}, status=400)


def _superusuario_requerido(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Inicia sesión para continuar.'}, status=401)
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Esta acción requiere permisos de superusuario.'}, status=403)
        return view(request, *args, **kwargs)
    return wrapped


def _validar_perfil(nombre, apellido, dni, correo, telefono):
    if not all((nombre, apellido, dni, correo, telefono)):
        return 'Completa nombre, apellido, DNI, correo y teléfono.'
    if len(nombre) > 100 or len(apellido) > 100:
        return 'El nombre y el apellido admiten hasta 100 caracteres.'
    if not re.fullmatch(r'\d{8}', dni):
        return 'El DNI debe tener exactamente 8 dígitos.'
    if not re.fullmatch(r'[^@\s]+@(tecsup\.edu\.pe|gmail\.com)', correo, flags=re.IGNORECASE):
        return 'Usa un correo @tecsup.edu.pe o @gmail.com.'
    if not re.fullmatch(r'\d{9}', telefono):
        return 'El teléfono debe tener exactamente 9 dígitos.'
    return None


def _perfil_json(perfil):
    cuenta = perfil.cuenta
    resultado = {
        'id': perfil.id,
        'nombre': perfil.nombre,
        'apellido': perfil.apellido,
        'dni': perfil.dni or '',
        'correo': perfil.correo or (cuenta.email if cuenta else ''),
        'telefono': perfil.telefono,
        'rol': perfil.rol,
        'rol_nombre': perfil.get_rol_display() or 'Sin asignar',
        'permisos': perfil.permisos,
        'protegida': bool(cuenta and cuenta.is_superuser),
        'estado': 'Activa' if cuenta and cuenta.is_active else 'Inactiva',
        'tiene_cuenta': cuenta is not None,
    }
    if perfil.rol == 'medico':
        try:
            medico = perfil.perfil_medico
        except Medico.DoesNotExist:
            medico = None
        resultado.update({
            'fecha_nacimiento': medico.fecha_nacimiento.isoformat() if medico and medico.fecha_nacimiento else '',
            'edad': medico.edad if medico else None,
            'identificacion_complementaria': medico.identificacion_complementaria if medico else '',
            'sexo': medico.sexo if medico else '',
            'especialidad': medico.especialidad if medico else '',
            'cmp': medico.cmp if medico and medico.cmp else '',
            'direccion': medico.direccion if medico else '',
        })
    elif perfil.rol == 'paciente':
        try:
            paciente = perfil.perfil_paciente
        except Paciente.DoesNotExist:
            paciente = None
        resultado.update({
            'fecha_nacimiento': paciente.fecha_nacimiento.isoformat() if paciente and paciente.fecha_nacimiento else '',
            'edad': paciente.edad if paciente else None,
            'sexo': paciente.sexo if paciente else '',
            'direccion': paciente.direccion if paciente else '',
            'informacion_contacto': paciente.informacion_contacto if paciente else '',
            'tipo_sangre': paciente.tipo_sangre if paciente else '',
            'contacto_emergencia': paciente.contacto_emergencia if paciente else '',
            'telefono_emergencia': paciente.telefono_emergencia if paciente else '',
        })
    return resultado


def _validar_datos_rol(rol, datos, perfil=None):
    fecha_nacimiento = parse_date(str(datos.get('fecha_nacimiento', '')).strip())
    if fecha_nacimiento is None:
        return 'Ingresa una fecha de nacimiento valida.'
    if fecha_nacimiento > timezone.localdate():
        return 'La fecha de nacimiento no puede ser futura.'

    sexo = str(datos.get('sexo', '')).strip()
    opciones_sexo = dict(Medico.SEXO_CHOICES)
    if rol == 'medico' and not sexo:
        return 'Selecciona el sexo del medico.'
    if sexo and sexo not in opciones_sexo:
        return 'Selecciona una opcion valida para sexo.'

    if rol == 'medico':
        identificacion = str(datos.get('identificacion_complementaria', '')).strip()
        especialidad = str(datos.get('especialidad', '')).strip()
        cmp = str(datos.get('cmp', '')).strip()
        if len(identificacion) > 100:
            return 'La identificacion complementaria admite hasta 100 caracteres.'
        if not especialidad or len(especialidad) > 100:
            return 'Ingresa la especialidad medica.'
        if not cmp or len(cmp) > 20:
            return 'Ingresa un CMP valido.'
        medicos_cmp = Medico.objects.filter(cmp=cmp)
        if perfil:
            medicos_cmp = medicos_cmp.exclude(usuario=perfil)
        if medicos_cmp.exists():
            return 'Ya existe un medico con ese CMP.'
    elif rol == 'paciente':
        tipo_sangre = str(datos.get('tipo_sangre', '')).strip()
        if tipo_sangre and tipo_sangre not in dict(Paciente.TIPO_SANGRE_CHOICES):
            return 'Selecciona un tipo de sangre valido.'
        if len(str(datos.get('contacto_emergencia', '')).strip()) > 120:
            return 'El contacto de emergencia admite hasta 120 caracteres.'
        if len(str(datos.get('telefono_emergencia', '')).strip()) > 20:
            return 'El telefono de emergencia admite hasta 20 caracteres.'
    return None


def _guardar_datos_rol(perfil, datos):
    fecha_nacimiento = parse_date(str(datos.get('fecha_nacimiento', '')).strip())
    sexo = str(datos.get('sexo', '')).strip()
    direccion = str(datos.get('direccion', '')).strip()
    if perfil.rol == 'medico':
        medico, _ = Medico.objects.get_or_create(usuario=perfil)
        medico.fecha_nacimiento = fecha_nacimiento
        medico.identificacion_complementaria = str(datos.get('identificacion_complementaria', '')).strip()
        medico.sexo = sexo
        medico.especialidad = str(datos.get('especialidad', '')).strip()
        medico.cmp = str(datos.get('cmp', '')).strip() or None
        medico.direccion = direccion
        medico.save()
    elif perfil.rol == 'paciente':
        paciente, _ = Paciente.objects.get_or_create(usuario=perfil)
        paciente.fecha_nacimiento = fecha_nacimiento
        paciente.sexo = sexo
        paciente.direccion = direccion
        paciente.informacion_contacto = str(datos.get('informacion_contacto', '')).strip()
        paciente.tipo_sangre = str(datos.get('tipo_sangre', '')).strip()
        paciente.contacto_emergencia = str(datos.get('contacto_emergencia', '')).strip()
        paciente.telefono_emergencia = str(datos.get('telefono_emergencia', '')).strip()
        paciente.save()


def _sincronizar_perfil_rol(perfil):
    if perfil.rol == 'medico':
        Medico.objects.get_or_create(usuario=perfil)
    elif perfil.rol == 'paciente':
        Paciente.objects.get_or_create(usuario=perfil)


@ensure_csrf_cookie
@require_GET
def obtener_csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})


@require_POST
def iniciar_sesion_admin(request):
    datos = _json_body(request)
    if datos is None:
        return _error_json()

    identificador = str(datos.get('usuario', '')).strip()
    contrasena = datos.get('contrasena', '')
    if not identificador or not isinstance(contrasena, str) or not contrasena:
        return JsonResponse({'error': 'Escribe tu usuario y contraseña.'}, status=400)

    User = get_user_model()
    cuenta = User.objects.filter(username__iexact=identificador).first()
    if cuenta is None:
        cuenta = User.objects.filter(email__iexact=identificador).first()
    if cuenta is None or not cuenta.is_superuser:
        return JsonResponse({'error': 'El usuario o la contraseña no son correctos.'}, status=401)

    if not cuenta.is_active:
        return JsonResponse({'error': 'La cuenta está inactiva.'}, status=403)

    usuario_autenticado = authenticate(request, username=cuenta.get_username(), password=contrasena)
    if usuario_autenticado is None or not usuario_autenticado.is_superuser:
        return JsonResponse({'error': 'El usuario o la contraseña no son correctos.'}, status=401)

    login(request, usuario_autenticado)
    return JsonResponse({
        'usuario': usuario_autenticado.get_username(),
        'csrfToken': get_token(request),
    })


@require_GET
def sesion_admin(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'No hay una sesión de administrador activa.'}, status=401)
    return JsonResponse({'usuario': request.user.get_username()})


@require_POST
def cerrar_sesion_admin(request):
    logout(request)
    return JsonResponse({'mensaje': 'Sesión cerrada.', 'csrfToken': get_token(request)})


@require_http_methods(['GET', 'POST'])
@_superusuario_requerido
def administrar_cuentas(request):
    if request.method == 'GET':
        perfiles = Usuario.objects.select_related('cuenta', 'perfil_medico', 'perfil_paciente').order_by('apellido', 'nombre')
        return JsonResponse({'cuentas': [_perfil_json(perfil) for perfil in perfiles]})

    datos = _json_body(request)
    if datos is None:
        return _error_json()

    nombre = str(datos.get('nombre', '')).strip()
    apellido = str(datos.get('apellido', '')).strip()
    dni = str(datos.get('dni', '')).strip()
    correo = str(datos.get('correo', '')).strip().lower()
    telefono = str(datos.get('telefono', '')).strip()
    rol = str(datos.get('rol', '')).strip()
    permisos = datos.get('permisos', [])
    contrasena = datos.get('contrasena', '')

    error = _validar_perfil(nombre, apellido, dni, correo, telefono)
    if error:
        return JsonResponse({'error': error}, status=400)
    if rol not in dict(Usuario.ROL_CHOICES):
        return JsonResponse({'error': 'Selecciona un rol válido.'}, status=400)
    error = _validar_permisos(rol, permisos)
    if error:
        return JsonResponse({'error': error}, status=400)
    error = _validar_datos_rol(rol, datos)
    if error:
        return JsonResponse({'error': error}, status=400)
    if not isinstance(contrasena, str) or not contrasena:
        return JsonResponse({'error': 'Escribe una contraseña inicial para la cuenta.'}, status=400)
    if Usuario.objects.filter(dni=dni).exists():
        return JsonResponse({'error': 'Ya existe un perfil con ese DNI.'}, status=409)

    User = get_user_model()
    if User.objects.filter(email__iexact=correo).exists():
        return JsonResponse({'error': 'Ya existe una cuenta con ese correo.'}, status=409)

    cuenta = User(username=correo, email=correo, first_name=nombre, last_name=apellido)
    try:
        validate_password(contrasena, user=cuenta)
    except ValidationError as exc:
        return JsonResponse({'error': ' '.join(exc.messages)}, status=400)

    try:
        with transaction.atomic():
            cuenta.set_password(contrasena)
            cuenta.save()
            perfil = Usuario.objects.create(
                cuenta=cuenta, nombre=nombre, apellido=apellido,
                dni=dni, correo=correo, telefono=telefono, rol=rol,
                permisos=permisos,
            )
            _sincronizar_perfil_rol(perfil)
            _guardar_datos_rol(perfil, datos)
    except IntegrityError:
        return JsonResponse({'error': 'No se pudo crear la cuenta: revisa si el correo o el DNI ya están registrados.'}, status=409)

    return JsonResponse({'cuenta': _perfil_json(perfil)}, status=201)


@require_http_methods(['GET', 'PATCH', 'DELETE'])
@_superusuario_requerido
def administrar_cuenta(request, cuenta_id):
    try:
        perfil = Usuario.objects.select_related('cuenta', 'perfil_medico', 'perfil_paciente').get(pk=cuenta_id)
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'No se encontró esa cuenta.'}, status=404)

    if perfil.cuenta and perfil.cuenta.is_superuser:
        return JsonResponse({'error': 'Las cuentas de superusuario no se administran desde este panel.'}, status=403)

    if request.method == 'GET':
        return JsonResponse({'cuenta': _perfil_json(perfil)})

    if request.method == 'DELETE':
        cuenta = perfil.cuenta
        if cuenta:
            cuenta.delete()
        else:
            perfil.delete()
        return JsonResponse({'mensaje': 'Cuenta eliminada.'})

    datos = _json_body(request)
    if datos is None:
        return _error_json()

    if 'activo' in datos:
        if not isinstance(datos['activo'], bool):
            return JsonResponse({'error': 'El estado debe ser activo o inactivo.'}, status=400)
        if not perfil.cuenta:
            return JsonResponse({'error': 'Este perfil no tiene una cuenta de acceso asociada.'}, status=400)
        perfil.cuenta.is_active = datos['activo']
        perfil.cuenta.save(update_fields=['is_active'])
        return JsonResponse({'cuenta': _perfil_json(perfil)})

    nombre = str(datos.get('nombre', '')).strip()
    apellido = str(datos.get('apellido', '')).strip()
    dni = str(datos.get('dni', '')).strip()
    correo = str(datos.get('correo', '')).strip().lower()
    telefono = str(datos.get('telefono', '')).strip()
    rol = str(datos.get('rol', '')).strip()
    permisos = datos.get('permisos', perfil.permisos)
    contrasena = datos.get('contrasena', '')
    error = _validar_perfil(nombre, apellido, dni, correo, telefono)
    if error:
        return JsonResponse({'error': error}, status=400)
    if rol not in dict(Usuario.ROL_CHOICES):
        return JsonResponse({'error': 'Selecciona un rol válido.'}, status=400)
    error = _validar_permisos(rol, permisos)
    if error:
        return JsonResponse({'error': error}, status=400)
    error = _validar_datos_rol(rol, datos, perfil)
    if error:
        return JsonResponse({'error': error}, status=400)
    if not isinstance(contrasena, str):
        return JsonResponse({'error': 'La nueva contraseña no es válida.'}, status=400)

    if Usuario.objects.filter(dni=dni).exclude(pk=perfil.pk).exists():
        return JsonResponse({'error': 'Ya existe un perfil con ese DNI.'}, status=409)
    if Usuario.objects.filter(correo__iexact=correo).exclude(pk=perfil.pk).exists():
        return JsonResponse({'error': 'Ya existe un perfil con ese correo.'}, status=409)

    User = get_user_model()
    cuentas_correo = User.objects.filter(email__iexact=correo)
    if perfil.cuenta:
        cuentas_correo = cuentas_correo.exclude(pk=perfil.cuenta.pk)
    if cuentas_correo.exists():
        return JsonResponse({'error': 'Ya existe una cuenta con ese correo.'}, status=409)

    if not perfil.cuenta and User.objects.filter(username__iexact=correo).exists():
        return JsonResponse({'error': 'Ya existe una cuenta con ese usuario.'}, status=409)

    cuenta_destino = perfil.cuenta or User(
        username=correo,
        email=correo,
        first_name=nombre,
        last_name=apellido,
        is_active=True,
    )
    if contrasena:
        try:
            validate_password(contrasena, user=cuenta_destino)
        except ValidationError as exc:
            return JsonResponse({'error': ' '.join(exc.messages)}, status=400)

    try:
        with transaction.atomic():
            perfil.nombre = nombre
            perfil.apellido = apellido
            perfil.dni = dni
            perfil.correo = correo
            perfil.telefono = telefono
            perfil.rol = rol
            perfil.permisos = permisos
            perfil.save()
            _sincronizar_perfil_rol(perfil)
            _guardar_datos_rol(perfil, datos)
            if perfil.cuenta or contrasena:
                cuenta_destino.first_name = nombre
                cuenta_destino.last_name = apellido
                cuenta_destino.email = correo
                cuenta_destino.username = correo
                campos = ['first_name', 'last_name', 'email', 'username']
                if contrasena:
                    cuenta_destino.set_password(contrasena)
                    campos.append('password')
                cuenta_destino.save(update_fields=campos) if perfil.cuenta else cuenta_destino.save()
                if not perfil.cuenta:
                    perfil.cuenta = cuenta_destino
                    perfil.save(update_fields=['cuenta'])
    except IntegrityError:
        return JsonResponse({'error': 'No se pudieron guardar los cambios: revisa el correo o el DNI.'}, status=409)

    return JsonResponse({'cuenta': _perfil_json(perfil)})
