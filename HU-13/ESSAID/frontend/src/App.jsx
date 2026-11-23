import React, { useEffect, useState } from 'react';
import { api, prepararSesion } from './api.js';
import AdminLayout from './components/AdminLayout.jsx';
import LoginAdmin from './components/LoginAdmin.jsx';
import HospitalesPage from './pages/HospitalesPage.jsx';
import ServiciosPage from './pages/ServiciosPage.jsx';
import CuentasPage from './pages/CuentasPage.jsx';
import { useRuta } from './useRuta.js';

const RUTA_CUENTAS = '/api/admin/cuentas/';
const RUTA_HOSPITALES = '/api/admin/hospitales/';
const RUTA_SERVICIOS = '/api/admin/servicios/';
const RUTA_ASIGNACIONES = RUTA_SERVICIOS + 'asignaciones/';

export default function App() {
  const [ruta, navegar] = useRuta();
  const [administrador, setAdministrador] = useState('');
  const [cuentas, setCuentas] = useState([]);
  const [hospitales, setHospitales] = useState([]);
  const [servicios, setServicios] = useState([]);
  const [asignaciones, setAsignaciones] = useState([]);
  const [totalCuentas, setTotalCuentas] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [errorLogin, setErrorLogin] = useState('');
  const [errorFormulario, setErrorFormulario] = useState('');
  const [errorHospital, setErrorHospital] = useState('');
  const [mensajeHospital, setMensajeHospital] = useState('');
  const [mensajeServicio, setMensajeServicio] = useState('');
  const [errorServicio, setErrorServicio] = useState('');
  const [mensajeAsignacion, setMensajeAsignacion] = useState('');
  const [errorAsignacion, setErrorAsignacion] = useState('');
  const [mensajeExito, setMensajeExito] = useState('');
  const [errorCargaDatos, setErrorCargaDatos] = useState('');

  async function cargarCuentas() {
    const resultado = await api(RUTA_CUENTAS);
    setCuentas(resultado.cuentas);
    setTotalCuentas(resultado.total);
  }

  async function cargarHospitales() {
    const resultado = await api(RUTA_HOSPITALES);
    setHospitales(resultado.hospitales);
  }

  async function cargarServicios() {
    const resultado = await api(RUTA_SERVICIOS);
    setServicios(resultado.servicios);
  }

  async function cargarAsignaciones() {
    const resultado = await api(RUTA_ASIGNACIONES);
    setAsignaciones(resultado.asignaciones);
  }

  useEffect(() => {
    let activa = true;
    async function prepararInicio() {
      try {
        await prepararSesion();
      } catch (error) {
        if (activa && error.status !== 401) setErrorLogin(error.message);
      } finally {
        if (activa) setCargando(false);
      }
    }
    prepararInicio();
    return () => { activa = false; };
  }, []);

  useEffect(() => {
    if (cargando) return;
    const pagina = new URL(ruta, window.location.origin).pathname.replace(/\/+$/, '') || '/';
    if (!administrador && pagina !== '/admin/login') navegar('/admin/login', true);
    else if (administrador && (pagina === '/' || pagina === '/admin/login')) navegar('/admin/cuentas', true);
  }, [administrador, cargando, navegar, ruta]);

  useEffect(() => {
    if (!administrador) return;
    const paginaActual = new URL(ruta, window.location.origin).pathname;
    const esHospitales = paginaActual.startsWith('/admin/hospitales');
    const esServicios = paginaActual.startsWith('/admin/servicios');
    if (!esHospitales && !esServicios) return;

    setErrorCargaDatos('');
    const solicitudes = [];
    if (esHospitales) solicitudes.push(cargarHospitales());
    if (esServicios) solicitudes.push(cargarServicios(), cargarAsignaciones());
    Promise.all(solicitudes).catch((error) => setErrorCargaDatos(error.message));
  }, [administrador, ruta]);

  async function iniciarSesion(credenciales) {
    setProcesando(true);
    setErrorLogin('');
    try {
      const sesion = await api('/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credenciales),
      });
      setAdministrador(sesion.usuario);
      await cargarCuentas();
      navegar('/admin/cuentas', true);
    } catch (error) {
      setErrorLogin(error.message);
    } finally {
      setProcesando(false);
    }
  }

  async function cerrarSesion() {
    setProcesando(true);
    try {
      await api('/api/auth/logout/', { method: 'POST' });
      setAdministrador('');
      setCuentas([]);
      setHospitales([]);
      setServicios([]);
      setAsignaciones([]);
      setTotalCuentas(0);
      navegar('/admin/login', true);
    } catch (error) {
      setErrorLogin(error.message);
    } finally {
      setProcesando(false);
    }
  }

  async function guardarCuenta(datos) {
    const editar = new URL(ruta, window.location.origin).pathname.match(/^\/admin\/cuentas\/(\d+)\/editar\/?$/);
    setProcesando(true);
    setErrorFormulario('');
    setMensajeExito('');
    try {
      const resultado = await api(editar ? `${RUTA_CUENTAS}${editar[1]}/` : RUTA_CUENTAS, {
        method: editar ? 'PATCH' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos),
      });
      if (editar) {
        setCuentas((actuales) => actuales.map((cuenta) => cuenta.id === Number(editar[1]) ? resultado.cuenta : cuenta));
        setMensajeExito(`Se guardaron los cambios de ${resultado.cuenta.nombre} ${resultado.cuenta.apellido}.`);
      } else {
        setCuentas((actuales) => [...actuales, resultado.cuenta]);
        setTotalCuentas((actual) => actual + 1);
      }
      navegar(`/admin/cuentas${new URL(ruta, window.location.origin).search}`);
    } catch (error) {
      setErrorFormulario(error.message);
    } finally {
      setProcesando(false);
    }
  }

  async function guardarHospital(datos) {
    const editarHospital = new URL(ruta, window.location.origin).pathname.match(/^\/admin\/hospitales\/(\d+)\/editar\/?$/);
    setProcesando(true);
    setErrorHospital('');
    setMensajeHospital('');
    try {
      const endpoint = editarHospital ? `${RUTA_HOSPITALES}${editarHospital[1]}/` : RUTA_HOSPITALES;
      const resultado = await api(endpoint, {
        method: editarHospital ? 'PATCH' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos),
      });
      if (editarHospital) {
        setHospitales((actuales) => actuales.map((hospital) => hospital.id === Number(editarHospital[1]) ? resultado.hospital : hospital).sort((a, b) => a.nombre.localeCompare(b.nombre)));
        setMensajeHospital(`Se guardaron los cambios del hospital ${resultado.hospital.nombre}.`);
        navegar('/admin/hospitales');
      } else {
        setHospitales((actuales) => [...actuales, resultado.hospital].sort((a, b) => a.nombre.localeCompare(b.nombre)));
        navegar('/admin/hospitales');
      }
    } catch (error) {
      setErrorHospital(error.message);
    } finally {
      setProcesando(false);
    }
  }

  async function cambiarEstadoHospital(hospital) {
    setProcesando(true);
    try {
      const nuevoEstado = !hospital.activo;
      const resultado = await api(`${RUTA_HOSPITALES}${hospital.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activo: nuevoEstado }),
      });
      setHospitales((actuales) => actuales.map((actual) => actual.id === hospital.id ? resultado.hospital : actual));
      setAsignaciones((actuales) => actuales.map((item) => item.hospital_id === hospital.id ? { ...item, hospital_activo: nuevoEstado } : item));
      setMensajeHospital(`El hospital ${hospital.nombre} ahora esta ${nuevoEstado ? 'activo' : 'inactivo'}.`);
    } catch (error) {
      window.alert(error.message);
    } finally {
      setProcesando(false);
    }
  }

  async function guardarServicio(datos) {
    const editarServicio = new URL(ruta, window.location.origin).pathname.match(/^\/admin\/servicios\/(\d+)\/editar\/?$/);
    setProcesando(true);
    setErrorServicio('');
    setMensajeServicio('');
    try {
      const endpoint = editarServicio ? `${RUTA_SERVICIOS}${editarServicio[1]}/` : RUTA_SERVICIOS;
      const resultado = await api(endpoint, {
        method: editarServicio ? 'PATCH' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos),
      });
      if (editarServicio) {
        setServicios((actuales) => actuales.map((servicio) => servicio.id === Number(editarServicio[1]) ? resultado.servicio : servicio));
        setAsignaciones((actuales) => actuales.map((item) => item.servicio_id === resultado.servicio.id ? { ...item, servicio_nombre: resultado.servicio.nombre, servicio_numero: resultado.servicio.numero, descripcion: resultado.servicio.descripcion } : item));
        setMensajeServicio(`Se guardaron los cambios del servicio ${resultado.servicio.nombre}.`);
      } else {
        setServicios((actuales) => [...actuales, resultado.servicio].sort((a, b) => a.numero - b.numero));
        setMensajeServicio(`Se agrego ${resultado.servicio.nombre} al catalogo.`);
      }
      navegar('/admin/servicios');
    } catch (error) {
      setErrorServicio(error.message);
    } finally {
      setProcesando(false);
    }
  }

  async function cambiarEstadoServicio(servicio) {
    setProcesando(true);
    try {
      const nuevoEstado = !servicio.activo;
      const resultado = await api(`${RUTA_SERVICIOS}${servicio.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activo: nuevoEstado }),
      });
      setServicios((actuales) => actuales.map((actual) => actual.id === servicio.id ? resultado.servicio : actual));
      setAsignaciones((actuales) => actuales.map((item) => item.servicio_id === servicio.id ? { ...item, servicio_activo: nuevoEstado } : item));
      setMensajeServicio(`El servicio ${servicio.nombre} ahora esta ${nuevoEstado ? 'activo' : 'inactivo'}.`);
    } catch (error) {
      window.alert(error.message);
    } finally {
      setProcesando(false);
    }
  }

  async function guardarAsignacion(datos) {
    setProcesando(true);
    setErrorAsignacion('');
    setMensajeAsignacion('');
    try {
      const resultado = await api(RUTA_ASIGNACIONES, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos),
      });
      setAsignaciones((actuales) => [...actuales, resultado.asignacion]);
      setMensajeAsignacion(`Se asigno ${resultado.asignacion.servicio_nombre} a ${resultado.asignacion.hospital_nombre}.`);
      navegar('/admin/servicios/asignados');
    } catch (error) {
      setErrorAsignacion(error.message);
    } finally {
      setProcesando(false);
    }
  }

  async function eliminarCuenta(cuenta) {
    if (!window.confirm(`Eliminar la cuenta de ${cuenta.nombre} ${cuenta.apellido}?`)) return;
    setProcesando(true);
    try {
      await api(`${RUTA_CUENTAS}${cuenta.id}/`, { method: 'DELETE' });
      setCuentas((actuales) => actuales.filter((actual) => actual.id !== cuenta.id));
      setTotalCuentas((actual) => Math.max(0, actual - 1));
    } catch (error) {
      window.alert(error.message);
    } finally {
      setProcesando(false);
    }
  }

  async function cambiarEstadoCuenta(cuenta) {
    setProcesando(true);
    try {
      const resultado = await api(`${RUTA_CUENTAS}${cuenta.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activo: cuenta.estado !== 'Activa' }),
      });
      setCuentas((actuales) => actuales.map((actual) => actual.id === cuenta.id ? resultado.cuenta : actual));
    } catch (error) {
      window.alert(error.message);
    } finally {
      setProcesando(false);
    }
  }

  if (!administrador) return <LoginAdmin onLogin={iniciarSesion} error={errorLogin} procesando={procesando || cargando} />;

  const urlRuta = new URL(ruta, window.location.origin);
  const pagina = urlRuta.pathname.replace(/\/+$/, '') || '/';
  const rutaLista = `/admin/cuentas${urlRuta.search}`;
  let contenido;
  const propsPagina = {
    pagina, urlRuta, rutaLista, navegar, procesando, errorCargaDatos,
    hospitales, servicios, asignaciones, cuentas, totalCuentas,
    mensajeHospital, mensajeServicio, mensajeAsignacion, mensajeExito,
    errorHospital, errorServicio, errorAsignacion, errorFormulario,
    guardarHospital, guardarServicio, guardarAsignacion, guardarCuenta,
    cambiarEstadoHospital, cambiarEstadoServicio, cambiarEstadoCuenta,
    eliminarCuenta,
  };
  if (pagina.startsWith('/admin/hospitales')) contenido = <HospitalesPage {...propsPagina} />;
  else if (pagina.startsWith('/admin/servicios')) contenido = <ServiciosPage {...propsPagina} />;
  else if (pagina.startsWith('/admin/cuentas')) contenido = <CuentasPage {...propsPagina} />;
  if (!contenido) contenido = <section className="admin-content"><h1>Pagina no encontrada</h1><button className="secondary-button" onClick={() => navegar('/admin/cuentas')}>Volver a las cuentas</button></section>;

  return <AdminLayout administrador={administrador} ruta={pagina} navegar={navegar} onLogout={cerrarSesion}>{contenido}</AdminLayout>;
}
