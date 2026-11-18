from django.db import models
from django.db.models.functions import Lower


class Hospital(models.Model):
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    contacto = models.CharField(max_length=100)
    servicios = models.ManyToManyField(
        'servicios.Servicio',
        through='servicios.HospitalServicio',
        related_name='hospitales',
        blank=True,
    )

    class Meta:
        db_table = 'usuarios_hospital'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(Lower('nombre'), name='uniq_hospital_nombre_ci'),
        ]

    def __str__(self):
        return self.nombre