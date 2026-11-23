from django.contrib import admin
from .models import Hospital


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'contacto')
    search_fields = ('nombre', 'direccion', 'contacto')