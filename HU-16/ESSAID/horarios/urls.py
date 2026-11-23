from django.urls import path

from . import views


urlpatterns = [
    path('', views.administrar_horarios, name='api-admin-horarios'),
    path('<int:horario_id>/', views.editar_horario, name='api-admin-horario'),
]
