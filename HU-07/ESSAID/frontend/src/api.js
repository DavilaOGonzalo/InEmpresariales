let csrfToken = '';

async function leerRespuesta(respuesta) {
  const texto = await respuesta.text();
  let datos = {};
  if (texto) {
    try {
      datos = JSON.parse(texto);
    } catch {
      throw new Error(`Django respondio algo inesperado (HTTP ${respuesta.status}). Revisa su terminal.`);
    }
  }
  if (!respuesta.ok) {
    const error = new Error(datos.error || `Error HTTP ${respuesta.status}.`);
    error.status = respuesta.status;
    throw error;
  }
  return datos;
}

export async function prepararSesion() {
  const respuesta = await fetch('/api/auth/csrf/', { credentials: 'include' });
  const datos = await leerRespuesta(respuesta);
  csrfToken = datos.csrfToken;
  return datos;
}

export async function api(ruta, opciones = {}) {
  const metodo = opciones.method || 'GET';
  const headers = { ...(opciones.headers || {}) };
  if (metodo !== 'GET' && csrfToken) headers['X-CSRFToken'] = csrfToken;
  const respuesta = await fetch(ruta, {
    ...opciones,
    method: metodo,
    headers,
    credentials: 'include',
  });
  const datos = await leerRespuesta(respuesta);
  if (datos.csrfToken) csrfToken = datos.csrfToken;
  return datos;
}
