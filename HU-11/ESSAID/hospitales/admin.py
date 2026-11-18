from django.contrib import admin
from .models import Hospital, ServicioMedico


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'contacto')
    search_fields = ('nombre', 'direccion', 'contacto')

@admin.register(ServicioMedico)
class ServicioMedicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'hospital')
    list_filter = ('hospital',)
    search_fields = ('nombre', 'hospital__nombre')