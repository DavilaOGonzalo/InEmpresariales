from django.db import models
from django.conf import settings
from django.utils import timezone


class Usuario(models.Model):
    ROL_CHOICES = [
        ('paciente', 'Paciente'),
        ('medico', 'Medico'),
    ]

    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_hospital',
        null=True,
        blank=True,
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True, null=True, blank=True)
    correo = models.EmailField(blank=True, null=True, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, blank=True, default='')
    permisos = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'


class Medico(models.Model):
    SEXO_CHOICES = [
        ('femenino', 'Femenino'),
        ('masculino', 'Masculino'),
        ('otro', 'Otro'),
        ('no_especificado', 'Prefiero no decir'),
    ]

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_medico',
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)
    identificacion_complementaria = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES, blank=True)
    especialidad = models.CharField(max_length=100, blank=True)
    cmp = models.CharField(max_length=20, unique=True, null=True, blank=True)
    direccion = models.TextField(blank=True)

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        hoy = timezone.localdate()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def __str__(self):
        return f'Medico: {self.usuario}'


class Paciente(models.Model):
    SEXO_CHOICES = Medico.SEXO_CHOICES
    TIPO_SANGRE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_paciente',
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES, blank=True)
    direccion = models.TextField(blank=True)
    informacion_contacto = models.TextField(blank=True)
    tipo_sangre = models.CharField(max_length=3, choices=TIPO_SANGRE_CHOICES, blank=True)
    contacto_emergencia = models.CharField(max_length=120, blank=True)
    telefono_emergencia = models.CharField(max_length=20, blank=True)

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        hoy = timezone.localdate()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def __str__(self):
        return f'Paciente: {self.usuario}'
