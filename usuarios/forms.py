from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Paciente, Usuario


class RegistroUsuarioForm(UserCreationForm):
    tipo_documento = forms.ChoiceField(
        choices=Paciente.TipoDocumento.choices,
        label="Tipo de documento",
        widget=forms.Select(attrs={"id": "id_tipo_documento"}),
    )
    numero_documento = forms.CharField(
        max_length=20,
        label="Número de documento",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
    caracter_verificador = forms.CharField(
        max_length=1,
        required=False,
        label="Carácter verificador",
        widget=forms.TextInput(attrs={"maxlength": "1", "autocomplete": "off"}),
    )
    fecha_nacimiento = forms.DateField(
        label="Fecha de nacimiento", widget=forms.DateInput(attrs={"type": "date"})
    )
    celular = forms.CharField(
        max_length=20,
        label="Celular",
        widget=forms.TelInput(attrs={"autocomplete": "tel"}),
    )
    terminos_aceptados = forms.BooleanField(
        required=True, label="Acepto los términos y condiciones de uso"
    )
    tratamiento_datos_autorizado = forms.BooleanField(
        required=True, label="Autorizo el tratamiento de mis datos personales"
    )

    class Meta:
        model = Usuario
        fields = ("email",)
        labels = {"email": "Correo electrónico"}
        widgets = {"email": forms.EmailInput(attrs={"autocomplete": "email"})}

    def clean_email(self):
        email = self.cleaned_data["email"]
        dominio = email.rsplit("@", 1)[-1].lower()
        if dominio not in {"gmail.com", "tecsup.edu.pe"}:
            raise forms.ValidationError(
                "Usa un correo que termine en @gmail.com o @tecsup.edu.pe."
            )
        return email

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo_documento")
        numero = cleaned_data.get("numero_documento", "").strip()
        verificador = cleaned_data.get("caracter_verificador", "").strip()

        if tipo == Paciente.TipoDocumento.DNI and not verificador:
            self.add_error(
                "caracter_verificador", "Ingresa el carácter verificador del DNI."
            )
        elif tipo == Paciente.TipoDocumento.CE and verificador:
            self.add_error(
                "caracter_verificador", "El CE no lleva carácter verificador."
            )

        if tipo and numero and Paciente.objects.filter(
            tipo_documento=tipo, numero_documento=numero
        ).exists():
            self.add_error(
                "numero_documento",
                "Ya existe un paciente con ese tipo y número de documento.",
            )

        cleaned_data["numero_documento"] = numero
        cleaned_data["caracter_verificador"] = verificador
        return cleaned_data
