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


class CrearUsuarioAdminForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Nombres")
    last_name = forms.CharField(max_length=150, label="Apellidos")
    tipo_documento = forms.ChoiceField(
        choices=[("", "Selecciona un tipo"), *Paciente.TipoDocumento.choices],
        required=False,
        label="Tipo de documento",
    )
    numero_documento = forms.CharField(
        max_length=20, required=False, label="Número de documento"
    )
    caracter_verificador = forms.CharField(
        max_length=1, required=False, label="Carácter verificador"
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    celular = forms.CharField(max_length=20, required=False, label="Celular")

    class Meta:
        model = Usuario
        fields = ("first_name", "last_name", "email", "rol")
        labels = {"email": "Correo electrónico", "rol": "Rol"}
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def __init__(self, *args, puede_crear_administrador=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not puede_crear_administrador:
            self.fields["rol"].choices = [
                choice
                for choice in self.fields["rol"].choices
                if choice[0] != Usuario.Rol.ADMINISTRADOR
            ]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get("rol")
        tipo = cleaned_data.get("tipo_documento")
        numero = cleaned_data.get("numero_documento", "").strip()
        verificador = cleaned_data.get("caracter_verificador", "").strip()

        if rol == Usuario.Rol.PACIENTE:
            for campo in (
                "tipo_documento",
                "numero_documento",
                "fecha_nacimiento",
                "celular",
            ):
                if not cleaned_data.get(campo):
                    self.add_error(campo, "Este campo es obligatorio para pacientes.")

            if tipo == Paciente.TipoDocumento.DNI and not verificador:
                self.add_error(
                    "caracter_verificador", "Ingresa el carácter verificador del DNI."
                )
            elif tipo == Paciente.TipoDocumento.CE and verificador:
                self.add_error(
                    "caracter_verificador", "El CE no lleva carácter verificador."
                )

            if tipo and numero and Paciente.objects.filter(
                tipo_documento=tipo, numero_documento__iexact=numero
            ).exists():
                self.add_error(
                    "numero_documento",
                    "Ya existe un paciente con ese tipo y número de documento.",
                )

        cleaned_data["numero_documento"] = numero
        cleaned_data["caracter_verificador"] = verificador
        return cleaned_data
