from django.db import models


class Cita(models.Model):
    ESTADO_PROGRAMADA = 'programada'
    ESTADO_CONFIRMADA = 'confirmada'
    ESTADO_COMPLETADA = 'completada'
    ESTADO_CANCELADA = 'cancelada'

    ESTADOS = [
        (ESTADO_PROGRAMADA, 'Programada'),
        (ESTADO_CONFIRMADA, 'Confirmada'),
        (ESTADO_COMPLETADA, 'Completada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]

    paciente = models.CharField(max_length=201)
    medico = models.CharField(max_length=201, db_index=True)
    fecha = models.DateField(db_index=True)
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PROGRAMADA, db_index=True)

    class Meta:
        db_table = 'citas'
        ordering = ['fecha', 'hora', 'id']
        verbose_name = 'cita'
        verbose_name_plural = 'citas'

    def __str__(self):
        return f'{self.paciente} - {self.medico} ({self.fecha} {self.hora})'
