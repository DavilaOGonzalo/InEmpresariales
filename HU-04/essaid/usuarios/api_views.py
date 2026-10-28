from django.db.models import QuerySet
from rest_framework import filters, generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Paciente, Usuario
from .serializers import PacienteSerializer, UsuarioSerializer


class IsAuthorizedAdmin(permissions.BasePermission):
    """Permite la API únicamente a administradores de la aplicación."""

    message = "Se requiere una sesión administrativa autorizada."

    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.is_staff
            and (usuario.is_superuser or usuario.rol == Usuario.Rol.ADMINISTRADOR)
        )


def _estado_filtrado(queryset: QuerySet, request):
    """Aplica ?estado=activo|inactivo a un queryset de usuarios o pacientes."""

    estado = request.query_params.get("estado")
    if estado is None or estado == "":
        return queryset

    valores = {
        "activo": True,
        "activa": True,
        "active": True,
        "true": True,
        "1": True,
        "inactivo": False,
        "inactiva": False,
        "inactive": False,
        "false": False,
        "0": False,
    }
    try:
        activo = valores[estado.strip().lower()]
    except KeyError as exc:
        raise ValidationError(
            {"estado": "Usa activo, inactivo, true, false, 1 o 0."}
        ) from exc

    if queryset.model is Paciente:
        return queryset.filter(usuario__is_active=activo)
    return queryset.por_estado(activo)


class UsuarioViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios con búsqueda, ordenamiento, estado y acción propia."""

    serializer_class = UsuarioSerializer
    permission_classes = (IsAuthorizedAdmin,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("email", "first_name", "last_name", "rol")
    ordering_fields = ("email", "first_name", "last_name", "rol", "is_active")
    ordering = ("last_name", "first_name", "email")

    def get_queryset(self):
        queryset = Usuario.objects.select_related("perfil_paciente").all()
        return _estado_filtrado(queryset, self.request).order_by(*self.ordering)

    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise ValidationError("No puedes eliminar la cuenta con la que estás conectado.")
        instance.delete()

    @action(detail=False, methods=("get",), url_path="activos")
    def activos(self, request):
        """Reutiliza UsuarioQuerySet.activos() mediante una acción del ViewSet."""

        queryset = self.filter_queryset(self.get_queryset().activos())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)


class PacienteViewSet(viewsets.ReadOnlyModelViewSet):
    """Consulta optimizada de pacientes con Usuario anidado."""

    serializer_class = PacienteSerializer
    permission_classes = (IsAuthorizedAdmin,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = (
        "numero_documento",
        "celular",
        "usuario__email",
        "usuario__first_name",
        "usuario__last_name",
    )
    ordering_fields = ("numero_documento", "fecha_nacimiento", "usuario__email")
    ordering = ("numero_documento",)

    def get_queryset(self):
        queryset = Paciente.objects.select_related("usuario").all()
        return _estado_filtrado(queryset, self.request).order_by(*self.ordering)


class UsuarioListCreateView(generics.ListCreateAPIView):
    """Versión con vista genérica solicitada para comparar con el ViewSet."""

    serializer_class = UsuarioSerializer
    permission_classes = (IsAuthorizedAdmin,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = UsuarioViewSet.search_fields
    ordering_fields = UsuarioViewSet.ordering_fields
    ordering = UsuarioViewSet.ordering

    def get_queryset(self):
        queryset = Usuario.objects.select_related("perfil_paciente").all()
        return _estado_filtrado(queryset, self.request).order_by(*self.ordering)


class UsuarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle CRUD con RetrieveUpdateDestroyAPIView."""

    serializer_class = UsuarioSerializer
    permission_classes = (IsAuthorizedAdmin,)

    def get_queryset(self):
        return Usuario.objects.select_related("perfil_paciente").all()

    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise ValidationError("No puedes eliminar la cuenta con la que estás conectado.")
        instance.delete()
