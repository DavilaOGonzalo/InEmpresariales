from django.contrib import admin

from .models import HorarioMedico


@admin.register(HorarioMedico)
class HorarioMedicoAdmin(admin.ModelAdmin):
    list_display = ('medico', 'fecha', 'hora_inicio', 'hora_fin', 'intervalo_minutos', 'activo')
    list_filter = ('activo', 'fecha')
    search_fields = ('medico__usuario__nombre', 'medico__usuario__apellido')
