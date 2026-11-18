from django.db import models
from django.db.models.functions import Lower


class Servicio(models.Model):
    numero = models.PositiveIntegerField(unique=True, editable=False)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['numero']
        constraints = [
            models.UniqueConstraint(Lower('nombre'), name='uniq_servicio_nombre_ci'),
        ]

    def __str__(self):
        return f'Servicio {self.numero}: {self.nombre}'


class HospitalServicio(models.Model):
    hospital = models.ForeignKey(
        'hospitales.Hospital',
        on_delete=models.CASCADE,
        related_name='relaciones_servicios',
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name='relaciones_hospitales',
    )

    class Meta:
        ordering = ['hospital__nombre', 'servicio__numero']
        constraints = [
            models.UniqueConstraint(
                fields=['hospital', 'servicio'],
                name='uniq_hospital_servicio',
            ),
        ]

    def __str__(self):
        return f'{self.servicio.nombre} - {self.hospital.nombre}'