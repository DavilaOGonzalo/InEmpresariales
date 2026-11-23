from django.urls import path
from . import views


urlpatterns = [
    path('', views.administrar_servicios, name='api-admin-servicios'),
    path('asignaciones/', views.administrar_asignaciones, name='api-admin-asignaciones'),
    path('<int:servicio_id>/', views.administrar_servicio, name='api-admin-servicio'),
]
