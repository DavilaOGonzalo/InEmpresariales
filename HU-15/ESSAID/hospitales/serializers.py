from rest_framework import serializers

from .models import Hospital


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ('id', 'nombre', 'direccion', 'contacto', 'activo')
        read_only_fields = ('id',)

    def validate_nombre(self, value):
        nombre = value.strip()
        hospitales = Hospital.objects.filter(nombre__iexact=nombre)
        if self.instance:
            hospitales = hospitales.exclude(pk=self.instance.pk)
        if hospitales.exists():
            raise serializers.ValidationError('Ya existe un hospital con ese nombre.')
        return nombre

    def validate_direccion(self, value):
        if not value.strip():
            raise serializers.ValidationError('Completa el nombre, la direccion y el contacto.')
        return value.strip()

    def validate_contacto(self, value):
        if not value.strip():
            raise serializers.ValidationError('Completa el nombre, la direccion y el contacto.')
        return value.strip()


class HospitalEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ('activo',)
