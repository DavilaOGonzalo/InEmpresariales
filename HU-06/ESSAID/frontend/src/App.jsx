import React, { useEffect, useState } from 'react';
import { api, prepararSesion } from './api.js';
import AdminLayout from './AdminLayout.jsx';
import CuentaForm from './CuentaForm.jsx';
import Cuentas from './Cuentas.jsx';
import LoginAdmin from './LoginAdmin.jsx';
import { useRuta } from './useRuta.js';

const RUTA_CUENTAS = '/api/admin/cuentas/';

export default function App() {
  const [ruta, navegar] = useRuta();
  const [administrador, setAdministrador] = useState('');
  const [cuentas, setCuentas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [errorLogin, setErrorLogin] = useState('');
  const [errorFormulario, setErrorFormulario] = useState('');
  const [mensajeExito, setMensajeExito] = useState('');

  async function cargarCuentas() {
    const resultado = await api(RUTA_CUENTAS);
    setCuentas(resultado.cuentas);
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
    const pagina = ruta.replace(/\/+$/, '') || '/';
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
      navegar('/admin/login', true);
    } catch (error) {
      setErrorLogin(error.message);
    } finally {
      setProcesando(false);
    }
  }

  async function guardarCuenta(datos) {
    const editar = ruta.match(/^\/admin\/cuentas\/(\d+)\/editar\/?$/);
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
      }
      navegar('/admin/cuentas');
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

  const pagina = ruta.replace(/\/+$/, '') || '/';
  const editar = pagina.match(/^\/admin\/cuentas\/(\d+)\/editar$/);
  const verMedico = pagina.match(/^\/admin\/cuentas\/(\d+)$/);
  let contenido;
  if (pagina === '/admin/cuentas/nueva') {
    contenido = <CuentaForm onSave={guardarCuenta} onCancel={() => navegar('/admin/cuentas')} error={errorFormulario} procesando={procesando} />;
  } else if (editar) {
    const cuenta = cuentas.find((item) => item.id === Number(editar[1]));
    contenido = cuenta
      ? <CuentaForm cuenta={cuenta} onSave={guardarCuenta} onCancel={() => navegar('/admin/cuentas')} error={errorFormulario} procesando={procesando} />
      : <section className="admin-content"><p className="form-error">No se encontro esa cuenta.</p><button className="secondary-button" onClick={() => navegar('/admin/cuentas')}>Volver a las cuentas</button></section>;
  } else if (verMedico) {
    const medico = cuentas.find((item) => item.id === Number(verMedico[1]) && item.rol === 'medico');
    contenido = medico
      ? <section className="admin-content"><div className="page-heading"><div><p className="eyebrow">PERFIL MEDICO</p><h1>{medico.nombre} {medico.apellido}</h1><p className="heading-copy">Consulta los datos registrados y su especialidad.</p></div></div><article className="account-form-card doctor-detail"><dl><div><dt>Especialidad</dt><dd>{medico.especialidad || 'Sin registrar'}</dd></div><div><dt>CMP</dt><dd>{medico.cmp || 'Sin registrar'}</dd></div><div><dt>DNI</dt><dd>{medico.dni || 'Sin registrar'}</dd></div><div><dt>Correo</dt><dd>{medico.correo || 'Sin registrar'}</dd></div><div><dt>Telefono</dt><dd>{medico.telefono || 'Sin registrar'}</dd></div><div><dt>Fecha de nacimiento</dt><dd>{medico.fecha_nacimiento || 'Sin registrar'}{medico.edad != null ? ` (${medico.edad} años)` : ''}</dd></div><div><dt>Sexo</dt><dd>{medico.sexo || 'Sin registrar'}</dd></div><div><dt>Direccion</dt><dd>{medico.direccion || 'Sin registrar'}</dd></div><div><dt>Estado</dt><dd>{medico.estado}</dd></div></dl><div className="account-form-actions"><button className="secondary-button" onClick={() => navegar('/admin/cuentas')}>Volver a la lista</button><button className="primary-button" onClick={() => navegar(`/admin/cuentas/${medico.id}/editar`)}>Editar medico</button></div></article></section>
      : <section className="admin-content"><p className="form-error">No se encontro ese medico.</p><button className="secondary-button" onClick={() => navegar('/admin/cuentas')}>Volver a las cuentas</button></section>;
  } else if (pagina === '/admin/cuentas') {
    contenido = <Cuentas cuentas={cuentas} navegar={navegar} onDelete={eliminarCuenta} onToggleStatus={cambiarEstadoCuenta} procesando={procesando} mensajeExito={mensajeExito} />;
  } else {
    contenido = <section className="admin-content"><h1>Pagina no encontrada</h1><button className="secondary-button" onClick={() => navegar('/admin/cuentas')}>Volver a las cuentas</button></section>;
  }

  return <AdminLayout administrador={administrador} ruta={pagina} navegar={navegar} onLogout={cerrarSesion}>{contenido}</AdminLayout>;
}
