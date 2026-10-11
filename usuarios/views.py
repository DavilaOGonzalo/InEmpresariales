from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import RegistroUsuarioForm
from .models import Paciente


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
