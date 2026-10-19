# EssAid · Laboratorio React y gestión administrativa

La carpeta `frontend` contiene el proyecto React creado con Vite para el
laboratorio de la Semana 9. La vista inicial **Laboratorio React** trabaja con
arreglos escritos a mano para demostrar JSX, expresiones, `map()`, `key`,
renderizado condicional, listas anidadas y estilos. Presenta las entidades
`Usuario` y `Paciente`; las consultas anidadas son datos de demostración y no
se consultan todavía en la API, tal como solicita el laboratorio.

También se conservan las vistas administrativas de EssAid: registro,
consulta/edición y estado de cuenta. Esas vistas sí consumen los endpoints
administrativos de Django descritos más abajo.

## Repositorio

https://github.com/DavilaOGonzalo/InEmpresariales

## Instalación y ejecución

```powershell
cd HU-04/frontend
node -v
npm -v
npm install
npm run dev
```

Abre <http://localhost:5173/> en el navegador. Para validar la entrega:

```powershell
npm run lint
npm run build
```

La aplicación se ejecuta como una SPA: `index.html` monta `src/main.jsx`,
`main.jsx` monta `App.jsx`, y `App.jsx` alterna la vista del laboratorio con
las pantallas administrativas. La interfaz pedagógica usa datos manuales para
mostrar `Usuario` y `Paciente`, una relación de consultas anidadas, el estado
`is_active`, una lista vacía y un importe calculado con JavaScript. La próxima
etapa consiste en reemplazar esos arreglos por llamadas a la API REST.

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

## Consulta y actualización administrativa

- `GET /api/gestion/usuarios/` lista las cuentas seleccionables.
- `GET /api/gestion/usuarios/<id>/` consulta los datos de una cuenta.
- `PATCH /api/gestion/usuarios/<id>/` actualiza únicamente nombres, apellidos,
  correo, rol y los datos del perfil paciente cuando el rol es `PACIENTE`.

La contraseña, permisos Django, flags de superusuario y consentimientos no
forman parte del contrato de actualización. Una cuenta que ya tiene perfil de
paciente conserva el rol `PACIENTE` para no desvincular sus datos.

## ADMIN-HU-03: estado de cuenta

La vista "Estado de cuenta" lista usuarios y consulta su estado con
`GET /api/gestion/usuarios/<id>/estado/`. Permite alternarlo mediante
`PATCH /api/gestion/usuarios/<id>/estado/` con `{"is_active": true}` o
`{"is_active": false}`. El backend solo autoriza superusuarios o usuarios staff
con rol `ADMINISTRADOR`; la interfaz no reemplaza esta validación.

Si el login está alojado en Spring Boot, Django no puede impedir por sí solo que
ese backend emita credenciales: Spring Boot debe consultar el mismo campo
`is_active` al autenticar y renovar tokens, y rechazar cuentas inactivas antes
de emitirlos. Esta copia no incluye el backend Spring Boot.

```powershell
npm install
npm run dev
```

La sesión administrativa es la sesión Django existente. Para probarla durante
el desarrollo, inicia sesión en `/admin/` a través del mismo servidor Vite y
luego abre el formulario.
