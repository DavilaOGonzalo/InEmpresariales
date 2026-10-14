import json

from django.test import TestCase
from django.urls import reverse

from .models import Paciente, Usuario


class RegistroUsuarioAdminTests(TestCase):
    def setUp(self):
        self.administrador = Usuario.objects.create_superuser(
            email="admin@essaid.test",
            password="AdminSeguro2026!",
            first_name="Admin",
            last_name="EssAid",
        )
        self.url = reverse("crear_usuario_admin_api")

    def post_json(self, datos):
        return self.client.post(
            self.url,
            data=json.dumps(datos),
            content_type="application/json",
        )

    def datos_paciente(self, **cambios):
        datos = {
            "first_name": "Ana",
            "last_name": "Pérez",
            "email": "ana@essaid.test",
            "password1": "ClaveSegura2026!",
            "password2": "ClaveSegura2026!",
            "rol": Usuario.Rol.PACIENTE,
            "tipo_documento": Paciente.TipoDocumento.DNI,
            "numero_documento": "12345678",
            "caracter_verificador": "9",
            "fecha_nacimiento": "1995-04-18",
            "celular": "999888777",
        }
        datos.update(cambios)
        return datos

    def test_registro_valido_asigna_rol_y_guarda_password_hasheada(self):
        self.client.force_login(self.administrador)

        respuesta = self.post_json(self.datos_paciente())

        self.assertEqual(respuesta.status_code, 201)
        usuario = Usuario.objects.get(email="ana@essaid.test")
        self.assertEqual(usuario.rol, Usuario.Rol.PACIENTE)
        self.assertTrue(usuario.check_password("ClaveSegura2026!"))
        self.assertNotEqual(usuario.password, "ClaveSegura2026!")
        self.assertEqual(usuario.perfil_paciente.numero_documento, "12345678")
        self.assertEqual(respuesta.json()["user"]["rol"], Usuario.Rol.PACIENTE)
        self.assertNotIn("password", respuesta.json()["user"])

    def test_campos_vacios_devuelven_errores_de_validacion(self):
        self.client.force_login(self.administrador)

        respuesta = self.post_json(
            {
                "first_name": "",
                "last_name": "",
                "email": "",
                "password1": "",
                "password2": "",
                "rol": Usuario.Rol.PACIENTE,
                "tipo_documento": "",
                "numero_documento": "",
                "caracter_verificador": "",
                "fecha_nacimiento": "",
                "celular": "",
            }
        )

        self.assertEqual(respuesta.status_code, 400)
        errores = respuesta.json()["errors"]
        for campo in (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "tipo_documento",
            "numero_documento",
            "fecha_nacimiento",
            "celular",
        ):
            self.assertIn(campo, errores)

    def test_correo_duplicado_no_crea_otra_cuenta(self):
        self.client.force_login(self.administrador)
        Usuario.objects.create_user(
            email="existente@essaid.test", password="OtraClave2026!"
        )

        respuesta = self.post_json(
            self.datos_paciente(email="EXISTENTE@ESSAID.TEST", numero_documento="87654321")
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("email", respuesta.json()["errors"])
        self.assertEqual(Usuario.objects.filter(email__iexact="existente@essaid.test").count(), 1)

    def test_documento_duplicado_no_crea_otra_cuenta(self):
        self.client.force_login(self.administrador)
        usuario = Usuario.objects.create_user(
            email="otro@essaid.test", password="OtraClave2026!"
        )
        Paciente.objects.create(
            usuario=usuario,
            tipo_documento=Paciente.TipoDocumento.DNI,
            numero_documento="12345678",
            caracter_verificador="8",
            fecha_nacimiento="1990-01-01",
            celular="999111222",
        )

        respuesta = self.post_json(
            self.datos_paciente(email="nuevo@essaid.test")
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("numero_documento", respuesta.json()["errors"])
        self.assertFalse(Usuario.objects.filter(email="nuevo@essaid.test").exists())
