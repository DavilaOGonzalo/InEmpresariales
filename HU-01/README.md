# EssAid — HU-01
HU-01 permite crear cuentas para pacientes y gestionar usuarios con distintos roles.

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
