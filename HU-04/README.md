# EssAid — HU-01, HU-02 y ADMIN-HU-03
Esta copia conserva HU-01 y HU-02, y añade la gestión administrativa del estado de cuenta.

## Registro del paciente

El paciente crea su cuenta en varios pasos: ingresa su correo y contraseña, completa sus datos personales y acepta los términos y el uso de sus datos. Al terminar, recibe una confirmación.

## Creación de usuarios por administración

El administrador registra una cuenta con nombre, correo, contraseña y rol. Si crea un paciente, también completa sus datos personales. El sistema avisa si el correo o el documento ya existen y muestra una confirmación cuando termina el registro.

## Contrato de registro administrativo

La operación está disponible para una sesión administrativa mediante `POST /api/gestion/usuarios/`. Usa los campos de `CrearUsuarioAdminForm`: `first_name`,
`last_name`, `email`, `password1`, `password2` y `rol`. Para el rol `PACIENTE`
son obligatorios además `tipo_documento`, `numero_documento`,
`fecha_nacimiento` y `celular`; `caracter_verificador` es obligatorio para DNI.

Una respuesta exitosa devuelve `201` con `{message, user}`. Los errores de
validación devuelven `400` con `{detail, errors}` y los mensajes agrupados por
campo.

## ADMIN-HU-02: consulta y actualización

La administración consulta usuarios con `GET /api/gestion/usuarios/` y el
detalle con `GET /api/gestion/usuarios/<id>/`. Los cambios se guardan mediante
`PATCH` usando únicamente nombres, apellidos, correo, rol y los datos del
perfil paciente cuando corresponda. La contraseña, permisos Django,
superusuario y consentimientos no son editables desde este flujo. Para
preservar el perfil existente, una cuenta con perfil de paciente conserva el
rol `PACIENTE`.

## ADMIN-HU-03: estado de cuenta

El usuario personalizado hereda `is_active` de Django `AbstractUser`; ese campo
existente es la fuente de verdad y no se agrega una columna duplicada. Django
Admin muestra el estado y permite editarlo desde la lista y el detalle solo a
superusuarios o usuarios `staff` con rol `ADMINISTRADOR`.

La consulta se realiza con `GET /api/gestion/usuarios/<id>/estado/` y el cambio
con `PATCH /api/gestion/usuarios/<id>/estado/`, enviando únicamente
`{"is_active": true}` o `{"is_active": false}`. La API exige un administrador
autorizado, valida CSRF en las modificaciones y devuelve `403` si el usuario no
tiene autorización o `400` si el cuerpo no contiene un booleano válido.
El estado no se expone en las respuestas generales de consulta ni se puede
cambiar mediante el endpoint general de edición.

El backend de autenticación predeterminado de Django (`ModelBackend`) rechaza
usuarios inactivos. Esta copia no incluye un login de usuario final ni backend
Spring Boot. Si Spring Boot gestiona el login de producción, deberá leer el
mismo `is_active` vigente antes de emitir sesiones o tokens y al renovarlos,
denegando el acceso a las cuentas inactivas (por ejemplo, `401` con código
`ACCOUNT_INACTIVE`). Django gestiona el estado; Spring Boot debe consultar la
fuente de verdad para evitar aceptar una réplica desactualizada. Esa integración
no se puede implementar ni verificar sin el backend Spring Boot.

## Base de datos

El proyecto usa MariaDB por defecto: `localhost:3306`, base `essaid_db` y
usuario `root`. La contraseña puede configurarse con `ESSAID_DB_PASSWORD`.
Instala las dependencias de Python desde `essaid/requirements.txt` antes de
ejecutar las migraciones.

## API REST con Django REST Framework

La aplicación también expone una API REST administrativa con Django REST Framework.
El acceso requiere una sesión Django de superusuario o de un usuario `staff` con
rol `ADMINISTRADOR`. Las modificaciones realizadas con sesión usan CSRF; para
pruebas desde un cliente HTTP también se puede utilizar autenticación básica.

### Instalación y ejecución

```powershell
cd essaid
python -m pip install -r requirements.txt
$env:ESSAID_DB_ENGINE = "django.db.backends.sqlite3"  # opcional para pruebas locales
python manage.py migrate
python manage.py test usuarios
python manage.py runserver
```

### Recursos y rutas DRF

El router está disponible bajo `/api/`:

- `/api/usuarios/`: `UsuarioViewSet` con CRUD completo.
- `/api/pacientes/`: `PacienteViewSet` de solo lectura, con el usuario relacionado
  anidado y `select_related("usuario")`.
- `/api/usuarios/activos/`: acción propia que reutiliza
  `UsuarioQuerySet.activos()`.
- `/api/generic/usuarios/` y `/api/generic/usuarios/<id>/`: comparación mediante
  `ListCreateAPIView` y `RetrieveUpdateDestroyAPIView`.

La colección de usuarios permite:

- búsqueda: `/api/usuarios/?search=ana`;
- ordenamiento: `/api/usuarios/?ordering=-email`;
- filtro de estado: `/api/usuarios/?estado=activo` o `?estado=inactivo`;
- combinación: `/api/usuarios/?estado=activo&search=gmail&ordering=email`.

Los serializers se encuentran en `essaid/usuarios/serializers.py`. Incluyen
`UsuarioSerializer`, `UsuarioResumenSerializer` y `PacienteSerializer`; el
serializer de usuario valida el correo con `validate_email`, guarda contraseñas
con `set_password` y no expone el campo `password` en las respuestas.

La API DRF convive con los endpoints administrativos anteriores bajo
`/api/gestion/usuarios/`, que siguen siendo consumidos por el frontend React.
