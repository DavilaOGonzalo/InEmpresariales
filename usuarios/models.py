from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class UsuarioManager(BaseUserManager):
    """Administra usuarios autenticados mediante una dirección de correo."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("El correo es obligatorio.")
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superusuario debe tener is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """Cuenta de EssAid; puede autenticarse con correo o vincular Google."""

    username = None
    email = models.EmailField("correo electrónico", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.email


class Paciente(models.Model):
    class TipoDocumento(models.TextChoices):
        DNI = "DNI", "DNI"
        CE = "CE", "Carné de extranjería"

    usuario = models.OneToOneField(
        "usuarios.Usuario",
        on_delete=models.CASCADE,
        related_name="perfil_paciente",
    )
    tipo_documento = models.CharField(
        "tipo de documento", max_length=3, choices=TipoDocumento.choices
    )
    numero_documento = models.CharField("número de documento", max_length=20)
    caracter_verificador = models.CharField(
        "carácter verificador", max_length=1, blank=True
    )
    fecha_nacimiento = models.DateField("fecha de nacimiento")
    celular = models.CharField("celular", max_length=20)
    terminos_aceptados = models.BooleanField(default=False)
    terminos_aceptados_en = models.DateTimeField(null=True, blank=True)
    tratamiento_datos_autorizado = models.BooleanField(default=False)
    tratamiento_datos_autorizado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "paciente"
        verbose_name_plural = "pacientes"
        constraints = [
            models.UniqueConstraint(
                fields=("tipo_documento", "numero_documento"),
                name="paciente_documento_unico",
            )
        ]

    def clean(self):
        super().clean()
        if self.tipo_documento == self.TipoDocumento.DNI and not self.caracter_verificador:
            raise ValidationError(
                {"caracter_verificador": "Es obligatorio para un DNI."}
            )
        if self.tipo_documento == self.TipoDocumento.CE and self.caracter_verificador:
            raise ValidationError(
                {"caracter_verificador": "No corresponde para un CE."}
            )

    def __str__(self):
        return f"Paciente {self.numero_documento} ({self.usuario.email})"
