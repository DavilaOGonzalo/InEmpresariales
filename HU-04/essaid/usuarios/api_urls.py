from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import (
    PacienteViewSet,
    UsuarioDetailView,
    UsuarioListCreateView,
    UsuarioViewSet,
)


router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="api-usuarios")
router.register(r"pacientes", PacienteViewSet, basename="api-pacientes")

urlpatterns = [
    path(
        "generic/usuarios/",
        UsuarioListCreateView.as_view(),
        name="api-generic-usuarios",
    ),
    path(
        "generic/usuarios/<int:pk>/",
        UsuarioDetailView.as_view(),
        name="api-generic-usuario-detail",
    ),
    path("", include(router.urls)),
]
