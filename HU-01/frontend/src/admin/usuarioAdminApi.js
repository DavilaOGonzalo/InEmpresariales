export const CREAR_USUARIO_ADMIN_URL = "/api/gestion/usuarios/";
export const CSRF_TOKEN_URL = "/api/gestion/usuarios/csrf/";

function getCookie(name) {
  if (typeof document === "undefined") return "";

  const cookie = document.cookie
    .split(";")
    .map((item) => item.trim())
    .find((item) => item.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.slice(name.length + 1)) : "";
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
  await fetchImpl(CSRF_TOKEN_URL, {
    method: "GET",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });

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

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.detail || "No se pudo registrar la cuenta.");
    error.status = response.status;
    error.errors = body.errors || {};
    throw error;
  }

  return body;
}
