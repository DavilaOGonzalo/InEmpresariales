from django.urls import path

from .views import consultar_disponibilidad


urlpatterns = [
    path('', consultar_disponibilidad, name='api-horarios-disponibles'),
]
