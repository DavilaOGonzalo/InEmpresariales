"""
URL configuration for essaid project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from usuarios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registro/', views.registro, name='registro'),
    path('registro/completado/', views.registro_completado, name='registro_completado'),
    path('gestion/usuarios/nuevo/', views.crear_usuario_admin, name='crear_usuario_admin'),
    path('gestion/usuarios/completado/', views.usuario_admin_completado, name='usuario_admin_completado'),
    path('api/gestion/usuarios/csrf/', views.csrf_token_api, name='csrf_token_api'),
    path('api/gestion/usuarios/', views.crear_usuario_admin_api, name='crear_usuario_admin_api'),
    path('api/gestion/usuarios/<int:usuario_id>/', views.usuario_admin_detalle_api, name='usuario_admin_detalle_api'),
]
