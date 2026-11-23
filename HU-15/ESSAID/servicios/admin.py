from django.contrib import admin
from .models import HospitalServicio, Servicio


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nombre')
    search_fields = ('nombre', 'descripcion')


@admin.register(HospitalServicio)
class HospitalServicioAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'hospital')
    list_filter = ('hospital',)
    search_fields = ('servicio__nombre', 'hospital__nombre')