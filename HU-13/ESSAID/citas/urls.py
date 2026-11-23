from django.urls import path

from . import views


urlpatterns = [
    path('', views.consultar_citas, name='api-admin-citas'),
]
