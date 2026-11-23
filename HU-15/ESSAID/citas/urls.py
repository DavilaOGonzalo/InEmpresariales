from django.urls import path

from . import views


urlpatterns = [
    path('', views.consultar_citas, name='api-admin-citas'),
    path('<int:cita_id>/estado/', views.cambiar_estado_cita, name='api-admin-cita-estado'),
]
