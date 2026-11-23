from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from .models import Hospital
from .serializers import HospitalEstadoSerializer, HospitalSerializer


def _first_error(errors):
    if isinstance(errors, dict) and errors:
        errors = next(iter(errors.values()))
    if isinstance(errors, (list, tuple)) and errors:
        return str(errors[0])
    return str(errors)


class IsSuperuser(BasePermission):
    message = 'Esta accion requiere permisos de superusuario.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class IsSessionAuthenticated(IsAuthenticated):
    message = 'Inicia sesion para continuar.'


class HospitalViewSet(viewsets.ViewSet):
    """API de administración de hospitales, conservando la forma JSON del frontend."""

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsSessionAuthenticated, IsSuperuser)

    def get_authenticate_header(self, request):
        # Mantiene 401 para sesiones ausentes, como la API anterior.
        return 'Session'

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response is not None:
            response.data = {'error': _first_error(response.data)}
        return response

    def _get_hospital(self, pk):
        try:
            return Hospital.objects.get(pk=pk)
        except (Hospital.DoesNotExist, ValueError):
            raise NotFound('No se encontro ese hospital.')

    def list(self, request):
        data = HospitalSerializer(Hospital.objects.all(), many=True).data
        return Response({'hospitales': data})

    def create(self, request):
        nombre = request.data.get('nombre')
        if isinstance(nombre, str) and Hospital.objects.filter(nombre__iexact=nombre.strip()).exists():
            return Response({'error': 'Ya existe un hospital con ese nombre.'}, status=status.HTTP_409_CONFLICT)
        serializer = HospitalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': _first_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                hospital = serializer.save()
        except IntegrityError:
            return Response({'error': 'Ya existe un hospital con ese nombre.'}, status=status.HTTP_409_CONFLICT)
        return Response(
            {'hospital': HospitalSerializer(hospital).data},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        hospital = self._get_hospital(pk)
        return Response({'hospital': HospitalSerializer(hospital).data})

    def partial_update(self, request, pk=None):
        hospital = self._get_hospital(pk)
        if set(request.data.keys()) == {'activo'}:
            serializer = HospitalEstadoSerializer(hospital, data=request.data, partial=True)
        else:
            nombre = request.data.get('nombre')
            if isinstance(nombre, str) and Hospital.objects.filter(nombre__iexact=nombre.strip()).exclude(pk=hospital.pk).exists():
                return Response({'error': 'Ya existe otro hospital con ese nombre.'}, status=status.HTTP_409_CONFLICT)
            serializer = HospitalSerializer(hospital, data=request.data)
        if not serializer.is_valid():
            return Response({'error': _first_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                hospital = serializer.save()
        except IntegrityError:
            return Response({'error': 'Ya existe otro hospital con ese nombre.'}, status=status.HTTP_409_CONFLICT)
        return Response({'hospital': HospitalSerializer(hospital).data})
