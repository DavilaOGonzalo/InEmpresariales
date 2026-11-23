from django.contrib import admin

from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'fecha', 'hora', 'estado')
    list_filter = ('fecha', 'estado', 'medico')
    search_fields = ('paciente', 'medico')
    ordering = ('fecha', 'hora')
