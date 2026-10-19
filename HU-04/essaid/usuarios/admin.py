from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Usuario


class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("email", "rol", "is_active", "is_staff")


class UsuarioChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = "__all__"


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    list_display = ("email", "first_name", "last_name", "rol", "is_active")
    list_filter = ("is_active", "rol")
    list_editable = ("is_active",)
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = (
        ("Cuenta", {"fields": ("email", "password")}),
        ("Datos personales", {"fields": ("first_name", "last_name", "rol")}),
        (
            "Permisos",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            "Crear cuenta",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "rol",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    @staticmethod
    def _puede_administrar_usuarios(request):
        usuario = request.user
        return usuario.is_superuser or (
            usuario.is_staff and usuario.rol == Usuario.Rol.ADMINISTRADOR
        )

    def has_module_permission(self, request):
        return self._puede_administrar_usuarios(request)

    def has_view_permission(self, request, obj=None):
        return self._puede_administrar_usuarios(request)

    def has_add_permission(self, request):
        return self._puede_administrar_usuarios(request)

    def has_change_permission(self, request, obj=None):
        return self._puede_administrar_usuarios(request)

    def has_delete_permission(self, request, obj=None):
        return self._puede_administrar_usuarios(request)
