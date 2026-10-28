import React, { useEffect, useState } from 'react';
import { api, prepararSesion } from './api.js';
import AdminLayout from './AdminLayout.jsx';
import CuentaForm from './CuentaForm.jsx';
import Cuentas from './Cuentas.jsx';
import LoginAdmin from './LoginAdmin.jsx';
import { useRuta } from './useRuta.js';

const CAMPOS_PERMISO = {
  'paciente.leer': 'Leer información de pacientes',
  'paciente.editar': 'Editar información de pacientes',
  'medico.leer_propio': 'Leer su propia información',
  'medico.editar_propio': 'Editar su propia información',
  'paciente.leer_propio': 'Leer su propia información',
  'paciente.editar_propio': 'Editar su propia información',
  'medico.leer': 'Leer información del médico',
};

function DetalleCuenta({ cuenta, rutaLista, urlRuta, navegar }) {
  const [tipoPermiso, setTipoPermiso] = useState('todos');
  const dato = (valor) => valor || 'Sin registrar';
  const permisos = Array.isArray(cuenta.permisos) ? cuenta.permisos : [];
  const tiposPermiso = [...new Set(permisos.map((permiso) => permiso.split('.')[0]))];
  const permisosVisibles = permisos.filter((permiso) => tipoPermiso === 'todos' || permiso.startsWith(`${tipoPermiso}.`));
  const grupos = [
    { titulo: 'Datos de cuenta', campos: [['DNI', cuenta.dni], ['Correo', cuenta.correo], ['Teléfono', cuenta.telefono], ['Rol', cuenta.rol_nombre], ['Estado', cuenta.estado]] },
    cuenta.rol === 'medico' && { titulo: 'Datos de médico', campos: [['Especialidad', cuenta.especialidad], ['CMP', cuenta.cmp], ['Fecha de nacimiento', cuenta.fecha_nacimiento], ['Edad', cuenta.edad != null ? `${cuenta.edad} años` : ''], ['Sexo', cuenta.sexo], ['Dirección', cuenta.direccion], ['Identificación complementaria', cuenta.identificacion_complementaria]] },
    cuenta.rol === 'paciente' && { titulo: 'Datos de paciente', campos: [['Fecha de nacimiento', cuenta.fecha_nacimiento], ['Edad', cuenta.edad != null ? `${cuenta.edad} años` : ''], ['Sexo', cuenta.sexo], ['Dirección', cuenta.direccion], ['Información de contacto', cuenta.informacion_contacto], ['Tipo de sangre', cuenta.tipo_sangre], ['Contacto de emergencia', cuenta.contacto_emergencia], ['Teléfono de emergencia', cuenta.telefono_emergencia]] },
  ].filter(Boolean);
  return <section className="admin-content"><div className="page-heading"><div><p className="eyebrow">DETALLE DE CUENTA</p><h1>{cuenta.nombre} {cuenta.apellido}</h1><p className="heading-copy">Consulta la información general de la cuenta.</p></div></div>
    {grupos.map((grupo) => <article className="account-form-card doctor-detail detail-section" key={grupo.titulo}><h2>{grupo.titulo}</h2><dl>{grupo.campos.map(([etiqueta, valor]) => <div key={etiqueta}><dt>{etiqueta}</dt><dd>{dato(valor)}</dd></div>)}</dl></article>)}
    <article className="account-form-card detail-section"><div className="detail-permissions-heading"><div><h2>Permisos asignados</h2><p className="permissions-copy">{cuenta.rol ? `Permisos correspondientes al rol ${cuenta.rol_nombre}.` : 'Esta cuenta no tiene un rol asignado.'}</p></div>{cuenta.rol && permisos.length > 0 && <label className="role-filter"><span>Tipo de permiso</span><select aria-label="Filtrar permisos por tipo" value={tipoPermiso} onChange={(evento) => setTipoPermiso(evento.target.value)}><option value="todos">Todos los tipos</option>{tiposPermiso.map((tipo) => <option key={tipo} value={tipo}>{tipo === 'medico' ? 'Médico' : tipo === 'paciente' ? 'Paciente' : tipo}</option>)}</select></label>}</div>
      {!cuenta.rol || permisos.length === 0 ? <p className="empty-permissions">No hay permisos para mostrar.</p> : permisosVisibles.length ? <ul className="detail-permission-list">{permisosVisibles.map((permiso) => <li key={permiso}><span>{CAMPOS_PERMISO[permiso] || permiso}</span><code>{permiso}</code></li>)}</ul> : <p className="empty-permissions">No hay permisos de este tipo.</p>}
    </article>
    <div className="account-form-actions"><button className="secondary-button" onClick={() => navegar(rutaLista)}>Volver a la lista</button><button className="primary-button" onClick={() => navegar(`/admin/cuentas/${cuenta.id}/editar${urlRuta.search}`)}>Editar cuenta</button></div>
  </section>;
}

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
    contenido = <Cuentas cuentas={cuentas} navegar={navegar} onDelete={eliminarCuenta} onToggleStatus={cambiarEstadoCuenta} procesando={procesando} mensajeExito={mensajeExito} consultaInicial={urlRuta.search} />;
  } else {
    contenido = <section className="admin-content"><h1>Pagina no encontrada</h1><button className="secondary-button" onClick={() => navegar('/admin/cuentas')}>Volver a las cuentas</button></section>;
  }

  return <AdminLayout administrador={administrador} ruta={pagina} navegar={navegar} onLogout={cerrarSesion}>{contenido}</AdminLayout>;
}
