from django.db import models
from django.db.models.functions import Lower


class Hospital(models.Model):
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    contacto = models.CharField(max_length=100)

    class Meta:
        db_table = 'usuarios_hospital'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(Lower('nombre'), name='uniq_hospital_nombre_ci'),
        ]

    def __str__(self):
        return self.nombre

class ServicioMedico(models.Model):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='servicios',
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['hospital__nombre', 'nombre']
        constraints = [
            models.UniqueConstraint(
                Lower('nombre'), 'hospital',
                name='uniq_servicio_hospital_nombre_ci',
            ),
        ]

    def __str__(self):
        return f'{self.nombre} - {self.hospital.nombre}'