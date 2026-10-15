export const CREAR_USUARIO_ADMIN_URL = "/api/gestion/usuarios/";
export const CSRF_TOKEN_URL = "/api/gestion/usuarios/csrf/";

const DETALLE_USUARIO_ADMIN_URL = (id) =>
  `${CREAR_USUARIO_ADMIN_URL}${encodeURIComponent(id)}/`;

function getCookie(name) {
  if (typeof document === "undefined") return "";

  const cookie = document.cookie
    .split(";")
    .map((item) => item.trim())
    .find((item) => item.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.slice(name.length + 1)) : "";
}

async function readResponse(response, defaultMessage) {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.detail || defaultMessage);
    error.status = response.status;
    error.errors = body.errors || {};
    throw error;
  }
  return body;
}

async function ensureCsrf(fetchImpl) {
  const response = await fetchImpl(CSRF_TOKEN_URL, {
    method: "GET",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  return readResponse(response, "No se pudo obtener el token CSRF.");
}

/**
 * Contrato compartido con CrearUsuarioAdminForm.
 * La API devuelve { message, user } en éxito y
 * { detail, errors: { campo: [mensajes] } } en error.
 */
export async function crearUsuarioAdmin(
  datos,
  { fetchImpl = fetch } = {},
) {
  await ensureCsrf(fetchImpl);

  const response = await fetchImpl(CREAR_USUARIO_ADMIN_URL, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(datos),
  });

  return readResponse(response, "No se pudo registrar la cuenta.");
}

export async function listarUsuariosAdmin({ fetchImpl = fetch } = {}) {
  const response = await fetchImpl(CREAR_USUARIO_ADMIN_URL, {
    method: "GET",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  return readResponse(response, "No se pudieron consultar los usuarios.");
}

export async function obtenerUsuarioAdmin(id, { fetchImpl = fetch } = {}) {
  const response = await fetchImpl(DETALLE_USUARIO_ADMIN_URL(id), {
    method: "GET",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  return readResponse(response, "No se pudo consultar el usuario.");
}

export async function actualizarUsuarioAdmin(
  id,
  datos,
  { fetchImpl = fetch } = {},
) {
  await ensureCsrf(fetchImpl);
  const response = await fetchImpl(DETALLE_USUARIO_ADMIN_URL(id), {
    method: "PATCH",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(datos),
  });
  return readResponse(response, "No se pudo actualizar la cuenta.");
}

export async function obtenerEstadoUsuarioAdmin(
  id,
  { fetchImpl = fetch } = {},
) {
  const response = await fetchImpl(`${DETALLE_USUARIO_ADMIN_URL(id)}estado/`, {
    method: "GET",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  return readResponse(response, "No se pudo consultar el estado de la cuenta.");
}

export async function cambiarEstadoUsuarioAdmin(
  id,
  isActive,
  { fetchImpl = fetch } = {},
) {
  await ensureCsrf(fetchImpl);
  const response = await fetchImpl(
    `${DETALLE_USUARIO_ADMIN_URL(id)}estado/`,
    {
      method: "PATCH",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ is_active: isActive }),
    },
  );
  return readResponse(response, "No se pudo cambiar el estado de la cuenta.");
}
