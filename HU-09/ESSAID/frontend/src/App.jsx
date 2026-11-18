import React, { useEffect, useState } from 'react';
import { api, prepararSesion } from './api.js';
import AdminLayout from './components/AdminLayout.jsx';
import CuentaForm from './components/CuentaForm.jsx';
import Cuentas from './components/Cuentas.jsx';
import DetalleCuenta from './components/DetalleCuenta.jsx';
import LoginAdmin from './components/LoginAdmin.jsx';
import { useRuta } from './useRuta.js';

const RUTA_CUENTAS = '/api/admin/cuentas/';

export default function App() {
  const [ruta, navegar] = useRuta();
  const [administrador, setAdministrador] = useState('');
  const [cuentas, setCuentas] = useState([]);
  const [totalCuentas, setTotalCuentas] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [errorLogin, setErrorLogin] = useState('');
  const [errorFormulario, setErrorFormulario] = useState('');
  const [mensajeExito, setMensajeExito] = useState('');

  async function cargarCuentas() {
    const resultado = await api(RUTA_CUENTAS);
    setCuentas(resultado.cuentas);
    setTotalCuentas(resultado.total);
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
  const editar = pagina.match(/^\/admin\/cuentas\/(\d+)\/editar$/);
  const verCuenta = pagina.match(/^\/admin\/cuentas\/(\d+)$/);
  let contenido;
  if (pagina === '/admin/cuentas/nueva') {
    contenido = <CuentaForm onSave={guardarCuenta} onCancel={() => navegar(rutaLista)} error={errorFormulario} procesando={procesando} />;
  } else if (editar) {
    const cuenta = cuentas.find((item) => item.id === Number(editar[1]));
    contenido = cuenta
      ? <CuentaForm cuenta={cuenta} onSave={guardarCuenta} onCancel={() => navegar(rutaLista)} error={errorFormulario} procesando={procesando} />
      : <section className="admin-content"><p className="form-error">No se encontro esa cuenta.</p><button className="secondary-button" onClick={() => navegar(rutaLista)}>Volver a las cuentas</button></section>;
  } else if (verCuenta) {
    const cuenta = cuentas.find((item) => item.id === Number(verCuenta[1]));
    contenido = cuenta
      ? <DetalleCuenta cuenta={cuenta} rutaLista={rutaLista} urlRuta={urlRuta} navegar={navegar} />
      : <section className="admin-content"><p className="form-error">No se encontro esa cuenta.</p><button className="secondary-button" onClick={() => navegar(rutaLista)}>Volver a las cuentas</button></section>;
  } else if (pagina === '/admin/cuentas') {
    contenido = <Cuentas cuentas={cuentas} totalCuentas={totalCuentas} navegar={navegar} onDelete={eliminarCuenta} onToggleStatus={cambiarEstadoCuenta} procesando={procesando} mensajeExito={mensajeExito} consultaInicial={urlRuta.search} />;
  } else {
    contenido = <section className="admin-content"><h1>Pagina no encontrada</h1><button className="secondary-button" onClick={() => navegar('/admin/cuentas')}>Volver a las cuentas</button></section>;
  }

  return <AdminLayout administrador={administrador} ruta={pagina} navegar={navegar} onLogout={cerrarSesion}>{contenido}</AdminLayout>;
}
