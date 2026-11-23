from django.core.exceptions import ValidationError
from django.db import models

from usuarios.models import Medico


class HorarioMedico(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='horarios')
    fecha = models.DateField(db_index=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    intervalo_minutos = models.PositiveSmallIntegerField(default=30)
    activo = models.BooleanField(default=True, db_index=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'horarios_medicos'
        ordering = ['fecha', 'hora_inicio', 'medico_id']
        constraints = [
            models.UniqueConstraint(
                fields=['medico', 'fecha', 'hora_inicio', 'hora_fin'],
                name='horario_medico_unico_rango',
            ),
        ]
        verbose_name = 'horario médico'
        verbose_name_plural = 'horarios médicos'

    def clean(self):
        errores = {}
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            errores['hora_fin'] = 'La hora final debe ser posterior a la hora inicial.'
        if not 5 <= self.intervalo_minutos <= 240:
            errores['intervalo_minutos'] = 'El intervalo debe estar entre 5 y 240 minutos.'
        if self.hora_inicio and self.hora_fin:
            minutos = (self.hora_fin.hour * 60 + self.hora_fin.minute) - (self.hora_inicio.hour * 60 + self.hora_inicio.minute)
            if minutos > 0 and self.intervalo_minutos and minutos % self.intervalo_minutos:
                errores['intervalo_minutos'] = 'El intervalo debe dividir exactamente el horario disponible.'
        if errores:
            raise ValidationError(errores)

    def __str__(self):
        return f'{self.medico} - {self.fecha} ({self.hora_inicio}-{self.hora_fin})'
