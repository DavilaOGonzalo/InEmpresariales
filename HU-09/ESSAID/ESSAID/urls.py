"""
URL configuration for mihostipal project.

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
    path('api/auth/csrf/', views.obtener_csrf, name='api-csrf'),
    path('api/auth/login/', views.iniciar_sesion_admin, name='api-admin-login'),
    path('api/auth/me/', views.sesion_admin, name='api-admin-session'),
    path('api/auth/logout/', views.cerrar_sesion_admin, name='api-admin-logout'),
    path('api/admin/cuentas/', views.administrar_cuentas, name='api-admin-cuentas'),
    path('api/admin/cuentas/<int:cuenta_id>/', views.administrar_cuenta, name='api-admin-cuenta'),
]
