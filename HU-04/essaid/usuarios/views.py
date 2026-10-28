import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods

from .forms import (
    ActualizarUsuarioAdminForm,
    CrearUsuarioAdminForm,
    RegistroUsuarioForm,
)
from .models import Paciente, Usuario


def _guardar_usuario_admin(form):
    """Guarda una cuenta administrativa y su perfil de paciente, si aplica.

    El formulario es la única fuente de validación para la vista HTML y la API.
    ``UserCreationForm.save`` usa ``set_password`` internamente, por lo que la
    contraseña nunca se persiste en texto plano.
    """
    with transaction.atomic():
        usuario = form.save(commit=False)
        usuario.is_staff = usuario.rol == Usuario.Rol.ADMINISTRADOR
        usuario.is_superuser = False
        usuario.save()

        if usuario.rol == Usuario.Rol.PACIENTE:
            paciente = Paciente(
                usuario=usuario,
                tipo_documento=form.cleaned_data["tipo_documento"],
                numero_documento=form.cleaned_data["numero_documento"],
                caracter_verificador=form.cleaned_data["caracter_verificador"],
                fecha_nacimiento=form.cleaned_data["fecha_nacimiento"],
                celular=form.cleaned_data["celular"],
            )
            paciente.full_clean()
            paciente.save()

    return usuario


def _conflicto_registro_admin(form, usuario=None, paciente=None):
    """Devuelve errores de unicidad detectados después de una carrera."""
    errores = {}
    email = form.cleaned_data.get("email")
    cuentas = Usuario.objects.filter(email__iexact=email) if email else Usuario.objects.none()
    if usuario is not None:
        cuentas = cuentas.exclude(pk=usuario.pk)
    if email and cuentas.exists():
        errores["email"] = "Ya existe una cuenta con ese correo."

    rol = form.cleaned_data.get("rol")
    tipo = form.cleaned_data.get("tipo_documento")
    numero = form.cleaned_data.get("numero_documento")
    if rol == Usuario.Rol.PACIENTE and tipo and numero:
        documentos = Paciente.objects.filter(
            tipo_documento=tipo, numero_documento__iexact=numero
        )
        if paciente is not None:
            documentos = documentos.exclude(pk=paciente.pk)
        if documentos.exists():
            errores["numero_documento"] = (
                "Ya existe un paciente con ese tipo y número de documento."
            )

    return errores


def _errores_formulario(form):
    return {
        campo: [str(error) for error in errores]
        for campo, errores in form.errors.items()
    }


def _datos_api(request):
    """Lee el contrato JSON y conserva compatibilidad con POST de formulario."""
    content_type = request.content_type or ""
    if "application/json" not in content_type:
        return request.POST.dict(), None

    try:
        datos = json.loads(request.body or b"{}")
    except (TypeError, ValueError):
        return None, "El cuerpo de la solicitud debe ser un JSON válido."

    if not isinstance(datos, dict):
        return None, "El cuerpo de la solicitud debe ser un objeto JSON."
    return datos, None


def _paciente_de_usuario(usuario):
    try:
        return usuario.perfil_paciente
    except Paciente.DoesNotExist:
        return None


def _usuario_admin_payload(usuario):
    paciente = _paciente_de_usuario(usuario)
    return {
        "id": usuario.pk,
        "first_name": usuario.first_name,
        "last_name": usuario.last_name,
        "email": usuario.email,
        "rol": usuario.rol,
        "has_patient": paciente is not None,
        "tipo_documento": paciente.tipo_documento if paciente else "",
        "numero_documento": paciente.numero_documento if paciente else "",
        "caracter_verificador": paciente.caracter_verificador if paciente else "",
        "fecha_nacimiento": (
            paciente.fecha_nacimiento.isoformat() if paciente else ""
        ),
        "celular": paciente.celular if paciente else "",
    }


def _requiere_sesion_administrativa(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse(
            {"detail": "Se requiere una sesión administrativa.", "errors": {}},
            status=403,
        )
    return None


def _requiere_administrador_autorizado(request):
    usuario = request.user
    if not usuario.is_authenticated or not usuario.is_staff or not (
        usuario.is_superuser or usuario.rol == Usuario.Rol.ADMINISTRADOR
    ):
        return JsonResponse(
            {"detail": "Se requiere un administrador autorizado.", "errors": {}},
            status=403,
        )
    return None


def _datos_actualizacion_usuario(usuario, paciente, datos):
    campos_autorizados = {
        "first_name",
        "last_name",
        "email",
        "rol",
        "tipo_documento",
        "numero_documento",
        "caracter_verificador",
        "fecha_nacimiento",
        "celular",
    }
    no_autorizados = sorted(set(datos) - campos_autorizados)
    if no_autorizados:
        return None, {
            campo: ["Este campo no está autorizado para actualización."]
            for campo in no_autorizados
        }

    actuales = _usuario_admin_payload(usuario)
    actuales.pop("id")
    actuales.pop("has_patient")
    actuales.update(datos)

    # Al cambiar un documento a CE, el carácter verificador anterior deja de
    # ser válido. Si el cliente omite ese campo en un PATCH, se limpia para
    # conservar la misma invariancia que exige Paciente.clean().
    if (
        actuales.get("rol") == Usuario.Rol.PACIENTE
        and actuales.get("tipo_documento") == Paciente.TipoDocumento.CE
        and "tipo_documento" in datos
        and "caracter_verificador" not in datos
    ):
        actuales["caracter_verificador"] = ""

    if (
        actuales.get("rol") != Usuario.Rol.PACIENTE
        and any(campo in datos for campo in ActualizarUsuarioAdminForm.CAMPOS_PACIENTE)
    ):
        return None, {
            "__all__": [
                "Los datos de paciente solo pueden modificarse para el rol PACIENTE."
            ]
        }

    return actuales, None


def _actualizar_usuario_admin(form):
    with transaction.atomic():
        usuario = form.instance
        usuario.first_name = form.cleaned_data["first_name"]
        usuario.last_name = form.cleaned_data["last_name"]
        usuario.email = form.cleaned_data["email"]
        usuario.rol = form.cleaned_data["rol"]
        usuario.is_staff = usuario.is_superuser or (
            usuario.rol == Usuario.Rol.ADMINISTRADOR
        )
        usuario.save(
            update_fields=("first_name", "last_name", "email", "rol", "is_staff")
        )

        if usuario.rol == Usuario.Rol.PACIENTE:
            paciente = form.paciente or Paciente(usuario=usuario)
            paciente.tipo_documento = form.cleaned_data["tipo_documento"]
            paciente.numero_documento = form.cleaned_data["numero_documento"]
            paciente.caracter_verificador = form.cleaned_data[
                "caracter_verificador"
            ]
            paciente.fecha_nacimiento = form.cleaned_data["fecha_nacimiento"]
            paciente.celular = form.cleaned_data["celular"]
            paciente.full_clean()
            paciente.save()

    return usuario


def _listar_usuarios_admin():
    usuarios = Usuario.objects.all().order_by("last_name", "first_name", "email")
    return {
        "users": [
            {
                "id": usuario.pk,
                "first_name": usuario.first_name,
                "last_name": usuario.last_name,
                "email": usuario.email,
                "rol": usuario.rol,
                "has_patient": _paciente_de_usuario(usuario) is not None,
            }
            for usuario in usuarios
        ]
    }


@require_GET
@ensure_csrf_cookie
def csrf_token_api(request):
    """Entrega la cookie CSRF para clientes React del mismo origen."""
    return JsonResponse({"detail": "Token CSRF disponible."})


def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                usuario = form.save()
                ahora = timezone.now()
                Paciente.objects.create(
                    usuario=usuario,
                    tipo_documento=form.cleaned_data["tipo_documento"],
                    numero_documento=form.cleaned_data["numero_documento"],
                    caracter_verificador=form.cleaned_data["caracter_verificador"],
                    fecha_nacimiento=form.cleaned_data["fecha_nacimiento"],
                    celular=form.cleaned_data["celular"],
                    terminos_aceptados=form.cleaned_data["terminos_aceptados"],
                    terminos_aceptados_en=ahora,
                    tratamiento_datos_autorizado=form.cleaned_data[
                        "tratamiento_datos_autorizado"
                    ],
                    tratamiento_datos_autorizado_en=ahora,
                )
            return redirect("registro_completado")
    else:
        form = RegistroUsuarioForm()

    campos_por_etapa = {
        1: {"email", "password1", "password2"},
        2: {"tipo_documento", "numero_documento", "caracter_verificador"},
        3: {"fecha_nacimiento"},
        4: {"celular"},
        5: {"terminos_aceptados", "tratamiento_datos_autorizado"},
    }
    etapa_actual = next(
        (
            etapa
            for etapa, campos in campos_por_etapa.items()
            if campos.intersection(form.errors.keys())
        ),
        1,
    )
    return render(
        request,
        "registration/registro.html",
        {"form": form, "etapa_actual": etapa_actual},
    )


def registro_completado(request):
    return render(request, "registration/registro_completado.html")


@staff_member_required
def crear_usuario_admin(request):
    puede_crear_administrador = request.user.is_superuser
    if request.method == "POST":
        form = CrearUsuarioAdminForm(
            request.POST,
            puede_crear_administrador=puede_crear_administrador,
        )
        if form.is_valid():
            try:
                usuario = _guardar_usuario_admin(form)
            except (IntegrityError, ValidationError):
                for campo, mensaje in _conflicto_registro_admin(form).items():
                    form.add_error(campo, mensaje)
                if not form.errors:
                    form.add_error(
                        None,
                        "No se pudo registrar la cuenta porque ya existe un dato igual.",
                    )
            else:
                messages.success(
                    request,
                    f"La cuenta de {usuario.email} se registró correctamente.",
                )
                return redirect("usuario_admin_completado")
    else:
        form = CrearUsuarioAdminForm(
            puede_crear_administrador=puede_crear_administrador,
        )

    return render(request, "usuarios/crear_usuario_admin.html", {"form": form})


@require_http_methods(["GET", "POST"])
def crear_usuario_admin_api(request):
    """Registra una cuenta administrativa para el formulario React Admin.

    Contrato de entrada: los mismos nombres de ``CrearUsuarioAdminForm``.
    Los datos de paciente son obligatorios únicamente cuando ``rol`` es
    ``PACIENTE``. La respuesta nunca incluye la contraseña.
    """
    respuesta_no_autorizada = _requiere_sesion_administrativa(request)
    if respuesta_no_autorizada is not None:
        return respuesta_no_autorizada

    if request.method == "GET":
        return JsonResponse(_listar_usuarios_admin())

    datos, error = _datos_api(request)
    if error:
        return JsonResponse(
            {"detail": error, "errors": {"__all__": [error]}}, status=400
        )

    form = CrearUsuarioAdminForm(
        datos,
        puede_crear_administrador=request.user.is_superuser,
    )
    if not form.is_valid():
        return JsonResponse(
            {
                "detail": "Revisa los datos enviados.",
                "errors": _errores_formulario(form),
            },
            status=400,
        )

    try:
        usuario = _guardar_usuario_admin(form)
    except (IntegrityError, ValidationError):
        errores = _conflicto_registro_admin(form)
        if not errores:
            errores = {
                "__all__": [
                    "No se pudo registrar la cuenta porque ya existe un dato igual."
                ]
            }
        return JsonResponse(
            {
                "detail": "No se pudo registrar la cuenta.",
                "errors": {campo: [mensaje] for campo, mensaje in errores.items()},
            },
            status=409,
        )

    return JsonResponse(
        {
            "message": f"La cuenta de {usuario.email} se registró correctamente.",
            "user": {
                "id": usuario.pk,
                "first_name": usuario.first_name,
                "last_name": usuario.last_name,
                "email": usuario.email,
                "rol": usuario.rol,
            },
        },
        status=201,
    )


@require_http_methods(["GET", "PATCH"])
def usuario_admin_detalle_api(request, usuario_id):
    """Consulta o actualiza los campos autorizados de un usuario."""
    respuesta_no_autorizada = _requiere_sesion_administrativa(request)
    if respuesta_no_autorizada is not None:
        return respuesta_no_autorizada

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse(
            {"detail": "Usuario no encontrado.", "errors": {}}, status=404
        )

    paciente = _paciente_de_usuario(usuario)
    if request.method == "GET":
        return JsonResponse({"user": _usuario_admin_payload(usuario)})

    datos, error = _datos_api(request)
    if error:
        return JsonResponse(
            {"detail": error, "errors": {"__all__": [error]}}, status=400
        )

    datos_completos, errores = _datos_actualizacion_usuario(
        usuario, paciente, datos
    )
    if errores:
        return JsonResponse(
            {"detail": "Revisa los campos autorizados.", "errors": errores},
            status=400,
        )

    form = ActualizarUsuarioAdminForm(
        datos_completos,
        instance=usuario,
        paciente=paciente,
        puede_crear_administrador=request.user.is_superuser,
    )
    if not form.is_valid():
        return JsonResponse(
            {
                "detail": "Revisa los datos enviados.",
                "errors": _errores_formulario(form),
            },
            status=400,
        )

    try:
        usuario = _actualizar_usuario_admin(form)
    except (IntegrityError, ValidationError):
        conflictos = _conflicto_registro_admin(form, usuario, paciente)
        if not conflictos:
            conflictos = {
                "__all__": [
                    "No se pudo actualizar la cuenta porque ya existe un dato igual."
                ]
            }
        return JsonResponse(
            {
                "detail": "No se pudo actualizar la cuenta.",
                "errors": {campo: [mensaje] for campo, mensaje in conflictos.items()},
            },
            status=409,
        )

    return JsonResponse(
        {
            "message": f"La cuenta de {usuario.email} se actualizó correctamente.",
            "user": _usuario_admin_payload(usuario),
        }
    )


@require_http_methods(["GET", "PATCH"])
def usuario_admin_estado_api(request, usuario_id):
    """Consulta el estado de una cuenta para administradores autorizados."""
    respuesta_no_autorizada = _requiere_administrador_autorizado(request)
    if respuesta_no_autorizada is not None:
        return respuesta_no_autorizada

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse(
            {"detail": "Usuario no encontrado.", "errors": {}}, status=404
        )

    if request.method == "GET":
        return JsonResponse(
            {
                "user": {
                    "id": usuario.pk,
                    "email": usuario.email,
                    "is_active": usuario.is_active,
                }
            }
        )

    datos, error = _datos_api(request)
    if error:
        return JsonResponse(
            {"detail": error, "errors": {"__all__": [error]}}, status=400
        )
    if set(datos) != {"is_active"} or type(datos["is_active"]) is not bool:
        mensaje = "Envía únicamente el campo is_active con un valor booleano."
        return JsonResponse(
            {"detail": mensaje, "errors": {"is_active": [mensaje]}}, status=400
        )

    usuario.is_active = datos["is_active"]
    usuario.save(update_fields=("is_active",))
    estado = "activada" if usuario.is_active else "desactivada"
    return JsonResponse(
        {
            "message": f"La cuenta de {usuario.email} fue {estado} correctamente.",
            "user": {
                "id": usuario.pk,
                "email": usuario.email,
                "is_active": usuario.is_active,
            },
        }
    )


@staff_member_required
def usuario_admin_completado(request):
    return render(request, "usuarios/usuario_admin_completado.html")
