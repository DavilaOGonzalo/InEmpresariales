from rest_framework import serializers

from .models import Paciente, Usuario


class PacienteResumenSerializer(serializers.ModelSerializer):
    """Representación breve para anidar un paciente dentro de un usuario."""

    class Meta:
        model = Paciente
        fields = (
            "id",
            "tipo_documento",
            "numero_documento",
            "caracter_verificador",
            "fecha_nacimiento",
            "celular",
        )


class UsuarioResumenSerializer(serializers.ModelSerializer):
    """Datos de cuenta usados dentro del recurso Paciente."""

    class Meta:
        model = Usuario
        fields = ("id", "email", "first_name", "last_name", "rol", "is_active")


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer CRUD de cuentas para la API administrativa."""

    paciente = PacienteResumenSerializer(source="perfil_paciente", read_only=True)
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = Usuario
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "rol",
            "is_active",
            "paciente",
        )
        read_only_fields = ("id", "is_active", "paciente")

    def validate_email(self, value):
        """Evita cuentas duplicadas aunque cambie el uso de mayúsculas."""

        email = value.strip().lower()
        cuentas = Usuario.objects.filter(email__iexact=email)
        if self.instance is not None:
            cuentas = cuentas.exclude(pk=self.instance.pk)
        if cuentas.exists():
            raise serializers.ValidationError(
                "Ya existe una cuenta con ese correo."
            )
        return email

    def validate_rol(self, value):
        request = self.context.get("request")
        if (
            value == Usuario.Rol.ADMINISTRADOR
            and request is not None
            and not request.user.is_superuser
        ):
            raise serializers.ValidationError(
                "Solo un superusuario puede crear o asignar administradores."
            )
        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError(
                {"password": "La contraseña es obligatoria al crear una cuenta."}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        rol = validated_data.get("rol", Usuario.Rol.PACIENTE)
        usuario = Usuario(
            **validated_data,
            is_staff=rol == Usuario.Rol.ADMINISTRADOR,
            is_superuser=False,
        )
        usuario.set_password(password)
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        if password:
            instance.set_password(password)
        instance.is_staff = instance.is_superuser or (
            instance.rol == Usuario.Rol.ADMINISTRADOR
        )
        instance.save()
        return instance


class PacienteSerializer(serializers.ModelSerializer):
    """Recurso de solo lectura con la cuenta relacionada anidada."""

    usuario = UsuarioResumenSerializer(read_only=True)

    class Meta:
        model = Paciente
        fields = (
            "id",
            "usuario",
            "tipo_documento",
            "numero_documento",
            "caracter_verificador",
            "fecha_nacimiento",
            "celular",
            "terminos_aceptados",
            "terminos_aceptados_en",
            "tratamiento_datos_autorizado",
            "tratamiento_datos_autorizado_en",
        )
        read_only_fields = fields
