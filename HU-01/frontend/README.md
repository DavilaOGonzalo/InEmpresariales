# Formulario React de gestión

El formulario `src/admin/CrearUsuarioAdmin.jsx` consume el contrato Django:

- `POST /api/gestion/usuarios/`
- El cliente solicita antes `GET /api/gestion/usuarios/csrf/` para obtener la
  cookie CSRF de Django.
- Entrada: `first_name`, `last_name`, `email`, `password1`, `password2`, `rol`.
- Si `rol` es `PACIENTE`, también envía `tipo_documento`, `numero_documento`,
  `caracter_verificador` para DNI, `fecha_nacimiento` y `celular`.
- Éxito (`201`): `{ message, user }`.
- Validación (`400`): `{ detail, errors: { campo: [mensajes] } }`.

Las opciones de rol y los nombres de campo se toman del modelo/formulario Django;
el backend sigue siendo la autoridad para permisos y validación.
El contenedor autenticado debe pasar `puedeCrearAdministrador={true}` solo para
superusuarios; el componente oculta ese rol por defecto.

```powershell
npm install
npm run dev
```

La sesión administrativa es la sesión Django existente. Para probarla durante
el desarrollo, inicia sesión en `/admin/` a través del mismo servidor Vite y
luego abre el formulario.
