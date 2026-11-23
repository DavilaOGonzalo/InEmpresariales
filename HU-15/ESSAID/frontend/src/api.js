import axios from 'axios';

let csrfToken = '';

const cliente = axios.create({
  withCredentials: true,
});

function manejarError(error) {
  const status = error.response?.status;
  const mensaje = error.response?.data?.error
    || (status ? `Error HTTP ${status}.` : error.message);
  const errorApi = new Error(mensaje);
  if (status) errorApi.status = status;
  throw errorApi;
}

export async function prepararSesion() {
  try {
    const respuesta = await cliente.get('/api/auth/csrf/');
    const datos = respuesta.data;
    csrfToken = datos.csrfToken;
    return datos;
  } catch (error) {
    manejarError(error);
  }
}

export async function api(ruta, opciones = {}) {
  const metodo = (opciones.method || 'GET').toUpperCase();
  const headers = { ...(opciones.headers || {}) };
  if (metodo !== 'GET' && csrfToken) headers['X-CSRFToken'] = csrfToken;

  try {
    const respuesta = await cliente.request({
      ...opciones,
      url: ruta,
      method: metodo,
      headers,
      data: opciones.body,
      withCredentials: true,
    });
    const datos = respuesta.data ?? {};
    if (datos.csrfToken) csrfToken = datos.csrfToken;
    return datos;
  } catch (error) {
    manejarError(error);
  }
}
