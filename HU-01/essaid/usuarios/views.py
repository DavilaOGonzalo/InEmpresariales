import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .forms import CrearUsuarioAdminForm, RegistroUsuarioForm
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


def _conflicto_registro_admin(form):
    """Devuelve errores de unicidad detectados después de una carrera."""
    errores = {}
    email = form.cleaned_data.get("email")
    if email and Usuario.objects.filter(email__iexact=email).exists():
        errores["email"] = "Ya existe una cuenta con ese correo."

    rol = form.cleaned_data.get("rol")
    tipo = form.cleaned_data.get("tipo_documento")
    numero = form.cleaned_data.get("numero_documento")
    if (
        rol == Usuario.Rol.PACIENTE
        and tipo
        and numero
        and Paciente.objects.filter(
            tipo_documento=tipo, numero_documento__iexact=numero
        ).exists()
    ):
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


@require_POST
def crear_usuario_admin_api(request):
    """Registra una cuenta administrativa para el formulario React Admin.

    Contrato de entrada: los mismos nombres de ``CrearUsuarioAdminForm``.
    Los datos de paciente son obligatorios únicamente cuando ``rol`` es
    ``PACIENTE``. La respuesta nunca incluye la contraseña.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse(
            {"detail": "Se requiere una sesión administrativa.", "errors": {}},
            status=403,
        )

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


@staff_member_required
def usuario_admin_completado(request):
    return render(request, "usuarios/usuario_admin_completado.html")
