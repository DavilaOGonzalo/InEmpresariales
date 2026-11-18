from django.urls import path
from . import views


urlpatterns = [
    path('', views.administrar_hospitales, name='api-admin-hospitales'),
    path('<int:hospital_id>/', views.administrar_hospital, name='api-admin-hospital'),
    path('servicios/', views.administrar_servicios, name='api-admin-servicios'),
    path('servicios/<int:servicio_id>/', views.administrar_servicio, name='api-admin-servicio'),
]