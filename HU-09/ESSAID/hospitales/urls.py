from django.urls import path
from . import views


urlpatterns = [
    path('', views.administrar_hospitales, name='api-admin-hospitales'),
]