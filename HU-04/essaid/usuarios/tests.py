import json
from datetime import date

from django.contrib.auth import authenticate
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

    def test_endpoint_csrf_entrega_cookie_para_react(self):
        respuesta = self.client.get(reverse("csrf_token_api"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("csrftoken", respuesta.cookies)

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

    def crear_paciente_existente(self, email="consultado@essaid.test"):
        usuario = Usuario.objects.create_user(
            email=email,
            password="ClaveSegura2026!",
            first_name="Nombre",
            last_name="Original",
            rol=Usuario.Rol.PACIENTE,
        )
        Paciente.objects.create(
            usuario=usuario,
            tipo_documento=Paciente.TipoDocumento.DNI,
            numero_documento="44556677",
            caracter_verificador="8",
            fecha_nacimiento=date(1990, 1, 1),
            celular="999111222",
        )
        return usuario

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

    def test_consulta_lista_y_detalle_de_usuario(self):
        self.client.force_login(self.administrador)
        usuario = self.crear_paciente_existente()

        lista = self.client.get(self.url)
        detalle = self.client.get(
            reverse("usuario_admin_detalle_api", args=[usuario.pk])
        )

        self.assertEqual(lista.status_code, 200)
        self.assertEqual(detalle.status_code, 200)
        self.assertIn(
            {"id": usuario.pk, "email": usuario.email, "rol": usuario.rol,
             "first_name": "Nombre", "last_name": "Original", "has_patient": True},
            lista.json()["users"],
        )
        self.assertEqual(detalle.json()["user"]["numero_documento"], "44556677")

    def test_actualizacion_correcta_persiste_solo_campos_autorizados(self):
        self.client.force_login(self.administrador)
        usuario = self.crear_paciente_existente()
        url = reverse("usuario_admin_detalle_api", args=[usuario.pk])

        respuesta = self.client.patch(
            url,
            data=json.dumps(
                {
                    "first_name": "Nombre actualizado",
                    "celular": "999333444",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 200)
        usuario.refresh_from_db()
        usuario.perfil_paciente.refresh_from_db()
        self.assertEqual(usuario.first_name, "Nombre actualizado")
        self.assertEqual(usuario.perfil_paciente.celular, "999333444")
        self.assertEqual(usuario.last_name, "Original")
        self.assertTrue(usuario.check_password("ClaveSegura2026!"))

    def test_actualizar_tipo_documento_a_ce_limpia_verificador_anterior(self):
        self.client.force_login(self.administrador)
        usuario = self.crear_paciente_existente()
        url = reverse("usuario_admin_detalle_api", args=[usuario.pk])

        respuesta = self.client.patch(
            url,
            data=json.dumps({"tipo_documento": Paciente.TipoDocumento.CE}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 200)
        usuario.perfil_paciente.refresh_from_db()
        self.assertEqual(usuario.perfil_paciente.tipo_documento, Paciente.TipoDocumento.CE)
        self.assertEqual(usuario.perfil_paciente.caracter_verificador, "")

    def test_usuario_inexistente_devuelve_404(self):
        self.client.force_login(self.administrador)
        url = reverse("usuario_admin_detalle_api", args=[999999])

        respuesta = self.client.get(url)

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(respuesta.json()["detail"], "Usuario no encontrado.")

    def test_actualizacion_de_usuario_inexistente_devuelve_404(self):
        self.client.force_login(self.administrador)
        url = reverse("usuario_admin_detalle_api", args=[999999])

        respuesta = self.client.patch(
            url,
            data=json.dumps({"first_name": "No existe"}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(respuesta.json()["detail"], "Usuario no encontrado.")

    def test_datos_invalidos_no_se_persisten(self):
        self.client.force_login(self.administrador)
        usuario = Usuario.objects.create_user(
            email="profesional@essaid.test",
            password="ClaveSegura2026!",
            first_name="Profesional",
            last_name="Original",
            rol=Usuario.Rol.PROFESIONAL_SALUD,
        )
        url = reverse("usuario_admin_detalle_api", args=[usuario.pk])

        respuesta = self.client.patch(
            url,
            data=json.dumps({"email": "correo-invalido"}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("email", respuesta.json()["errors"])
        usuario.refresh_from_db()
        self.assertEqual(usuario.email, "profesional@essaid.test")

    def test_campo_no_autorizado_es_rechazado(self):
        self.client.force_login(self.administrador)
        usuario = Usuario.objects.create_user(
            email="sin-password-edit@essaid.test",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.PROFESIONAL_SALUD,
        )
        url = reverse("usuario_admin_detalle_api", args=[usuario.pk])

        respuesta = self.client.patch(
            url,
            data=json.dumps({"password": "NuevaClave2026!"}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("password", respuesta.json()["errors"])


class UsuarioAdminEstadoCuentaTests(TestCase):
    def test_django_admin_expone_is_active_a_superusuario(self):
        administrador = Usuario.objects.create_superuser(
            email="admin-estado@essaid.test",
            password="ClaveTemporal2026!",
        )
        self.client.force_login(administrador)

        respuesta = self.client.get("/admin/usuarios/usuario/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "is_active")

    def test_django_admin_restringe_usuarios_staff_no_administradores(self):
        usuario = Usuario.objects.create_user(
            email="staff-no-admin@essaid.test",
            password="ClaveTemporal2026!",
            rol=Usuario.Rol.PACIENTE,
            is_staff=True,
        )
        self.client.force_login(usuario)

        respuesta = self.client.get("/admin/usuarios/usuario/")

        self.assertEqual(respuesta.status_code, 403)


class ConsultaEstadoUsuarioAdminTests(TestCase):
    def setUp(self):
        self.administrador = Usuario.objects.create_superuser(
            email="consulta-admin@essaid.test",
            password="ClaveTemporal2026!",
        )
        self.usuario = Usuario.objects.create_user(
            email="consulta-cuenta@essaid.test",
            password="ClaveTemporal2026!",
        )
        self.url = reverse("usuario_admin_estado_api", args=[self.usuario.pk])

    def cambiar_estado(self, is_active):
        return self.client.patch(
            self.url,
            data=json.dumps({"is_active": is_active}),
            content_type="application/json",
        )

    def test_administrador_autorizado_puede_consultar_estado(self):
        self.client.force_login(self.administrador)

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json()["user"],
            {
                "id": self.usuario.pk,
                "email": self.usuario.email,
                "is_active": True,
            },
        )

    def test_staff_sin_rol_administrador_no_puede_consultar_estado(self):
        usuario_staff = Usuario.objects.create_user(
            email="consulta-staff@essaid.test",
            password="ClaveTemporal2026!",
            is_staff=True,
            rol=Usuario.Rol.PACIENTE,
        )
        self.client.force_login(usuario_staff)

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 403)
        self.assertTrue(Usuario.objects.get(pk=self.usuario.pk).is_active)

    def test_administrador_puede_desactivar_y_se_bloquea_autenticacion(self):
        self.client.force_login(self.administrador)

        respuesta = self.cambiar_estado(False)

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.json()["user"]["is_active"])
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.is_active)
        self.assertIsNone(
            authenticate(
                email="consulta-cuenta@essaid.test",
                password="ClaveTemporal2026!",
            )
        )

    def test_administrador_puede_activar_y_restaura_autenticacion(self):
        self.usuario.is_active = False
        self.usuario.save(update_fields=("is_active",))
        self.client.force_login(self.administrador)

        respuesta = self.cambiar_estado(True)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.json()["user"]["is_active"])
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.is_active)
        self.assertEqual(
            authenticate(
                email="consulta-cuenta@essaid.test",
                password="ClaveTemporal2026!",
            ),
            self.usuario,
        )

    def test_solo_is_active_booleano_puede_modificarse(self):
        self.client.force_login(self.administrador)

        respuesta = self.client.patch(
            self.url,
            data=json.dumps({"is_active": "false"}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.is_active)


class DjangoRestFrameworkApiTests(TestCase):
    def setUp(self):
        self.administrador = Usuario.objects.create_superuser(
            email="drf-admin@essaid.test",
            password="ClaveTemporal2026!",
            first_name="Admin",
            last_name="DRF",
        )
        self.usuario = Usuario.objects.create_user(
            email="consulta-drf@essaid.test",
            password="ClaveTemporal2026!",
            first_name="Consulta",
            last_name="DRF",
            rol=Usuario.Rol.PACIENTE,
        )
        self.paciente = Paciente.objects.create(
            usuario=self.usuario,
            tipo_documento=Paciente.TipoDocumento.DNI,
            numero_documento="77889900",
            caracter_verificador="1",
            fecha_nacimiento=date(1992, 2, 2),
            celular="999222333",
        )
        self.client.force_login(self.administrador)

    def json_get(self, url):
        return self.client.get(url, HTTP_ACCEPT="application/json")

    def json_post(self, url, data):
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
        )

    def json_patch(self, url, data):
        return self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
        )

    def test_router_expone_recursos(self):
        raiz = self.json_get("/api/")
        usuarios = self.json_get("/api/usuarios/")

        self.assertEqual(raiz.status_code, 200)
        self.assertIn("usuarios", raiz.json())
        self.assertIn("pacientes", raiz.json())
        self.assertEqual(usuarios.status_code, 200)
        self.assertTrue(
            any(item["email"] == self.usuario.email for item in usuarios.json())
        )

    def test_model_serializer_crea_usuario_y_hashea_password(self):
        respuesta = self.json_post(
            "/api/usuarios/",
            {
                "first_name": "Nuevo",
                "last_name": "Profesional",
                "email": "nuevo-drf@essaid.test",
                "password": "ClaveSegura2026!",
                "rol": Usuario.Rol.PROFESIONAL_SALUD,
            },
        )

        self.assertEqual(respuesta.status_code, 201)
        usuario = Usuario.objects.get(email="nuevo-drf@essaid.test")
        self.assertTrue(usuario.check_password("ClaveSegura2026!"))
        self.assertNotIn("password", respuesta.json())

    def test_validate_email_rechaza_duplicado(self):
        respuesta = self.json_post(
            "/api/usuarios/",
            {
                "email": self.usuario.email.upper(),
                "password": "OtraClave2026!",
            },
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("email", respuesta.json())

    def test_pacientes_devuelve_relacion_anidada_y_estado(self):
        respuesta = self.json_get("/api/pacientes/?estado=activo")

        self.assertEqual(respuesta.status_code, 200)
        paciente = next(
            item for item in respuesta.json() if item["id"] == self.paciente.pk
        )
        self.assertEqual(paciente["usuario"]["email"], self.usuario.email)
        self.assertTrue(paciente["usuario"]["is_active"])

    def test_busqueda_ordenamiento_filtro_y_accion(self):
        self.usuario.is_active = False
        self.usuario.save(update_fields=("is_active",))
        activo = Usuario.objects.create_user(
            email="activo-drf@essaid.test",
            password="ClaveTemporal2026!",
            first_name="Activo",
        )

        busqueda = self.json_get("/api/usuarios/?search=activo-drf")
        orden = self.json_get("/api/usuarios/?ordering=-email")
        inactivos = self.json_get("/api/usuarios/?estado=inactivo")
        activos = self.json_get("/api/usuarios/activos/")

        self.assertEqual(busqueda.status_code, 200)
        self.assertEqual(busqueda.json()[0]["id"], activo.pk)
        self.assertEqual(orden.status_code, 200)
        self.assertEqual(orden.json()[0]["email"], "drf-admin@essaid.test")
        self.assertEqual(inactivos.status_code, 200)
        self.assertIn(self.usuario.pk, [item["id"] for item in inactivos.json()])
        self.assertNotIn(self.usuario.pk, [item["id"] for item in activos.json()])

    def test_estado_invalido_devuelve_400(self):
        respuesta = self.json_get("/api/usuarios/?estado=desconocido")

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("estado", respuesta.json())

    def test_crud_del_viewset_devuelve_204_al_eliminar(self):
        detalle = f"/api/usuarios/{self.usuario.pk}/"

        self.assertEqual(self.json_get(detalle).status_code, 200)
        actualizacion = self.json_patch(detalle, {"first_name": "Actualizado"})
        self.assertEqual(actualizacion.status_code, 200)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.first_name, "Actualizado")

        self.usuario.perfil_paciente.delete()
        eliminacion = self.client.delete(detalle, HTTP_ACCEPT="application/json")
        self.assertEqual(eliminacion.status_code, 204)
        self.assertEqual(self.json_get(detalle).status_code, 404)

    def test_vistas_genericas_exponen_lista_y_detalle(self):
        lista = self.json_get("/api/generic/usuarios/")
        detalle = self.json_get(f"/api/generic/usuarios/{self.usuario.pk}/")
        creacion = self.json_post(
            "/api/generic/usuarios/",
            {
                "email": "generico-drf@essaid.test",
                "password": "ClaveSegura2026!",
                "rol": Usuario.Rol.PROFESIONAL_SALUD,
            },
        )

        self.assertEqual(lista.status_code, 200)
        self.assertEqual(detalle.status_code, 200)
        self.assertEqual(detalle.json()["email"], self.usuario.email)
        self.assertEqual(creacion.status_code, 201)

    def test_serializer_de_paciente_mide_la_optimizacion_select_related(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        from .serializers import PacienteSerializer

        with CaptureQueriesContext(connection) as consultas_sin_optimizar:
            datos_sin_optimizar = PacienteSerializer(
                Paciente.objects.all(), many=True
            ).data

        with CaptureQueriesContext(connection) as consultas_optimizadas:
            datos = PacienteSerializer(
                Paciente.objects.select_related("usuario"), many=True
            ).data

        self.assertEqual(len(datos), 1)
        self.assertEqual(len(datos_sin_optimizar), 1)
        self.assertEqual(datos[0]["usuario"]["email"], self.usuario.email)
        self.assertGreater(len(consultas_sin_optimizar), len(consultas_optimizadas))
        self.assertEqual(len(consultas_optimizadas), 1)

    def test_api_restringe_usuario_no_administrador(self):
        usuario_staff = Usuario.objects.create_user(
            email="staff-paciente-drf@essaid.test",
            password="ClaveTemporal2026!",
            rol=Usuario.Rol.PACIENTE,
            is_staff=True,
        )
        self.client.force_login(usuario_staff)

        respuesta = self.json_get("/api/usuarios/")

        self.assertEqual(respuesta.status_code, 403)
