import React, { useState } from 'react';

const CAMPOS_PERMISO = {
  'paciente.leer': 'Leer información de pacientes',
  'paciente.editar': 'Editar información de pacientes',
  'medico.leer_propio': 'Leer su propia información',
  'medico.editar_propio': 'Editar su propia información',
  'paciente.leer_propio': 'Leer su propia información',
  'paciente.editar_propio': 'Editar su propia información',
  'medico.leer': 'Leer información del médico',
};

export default function DetalleCuenta({ cuenta, rutaLista, urlRuta, navegar }) {
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

  return <section className="admin-content">
    <div className="page-heading"><div><p className="eyebrow">DETALLE DE CUENTA</p><h1>{cuenta.nombre} {cuenta.apellido}</h1><p className="heading-copy">Consulta la información general de la cuenta.</p></div></div>
    {grupos.map((grupo) => <article className="account-form-card doctor-detail detail-section" key={grupo.titulo}><h2>{grupo.titulo}</h2><dl>{grupo.campos.map(([etiqueta, valor]) => <div key={etiqueta}><dt>{etiqueta}</dt><dd>{dato(valor)}</dd></div>)}</dl></article>)}
    <article className="account-form-card detail-section"><div className="detail-permissions-heading"><div><h2>Permisos asignados</h2><p className="permissions-copy">{cuenta.rol ? `Permisos correspondientes al rol ${cuenta.rol_nombre}.` : 'Esta cuenta no tiene un rol asignado.'}</p></div>{cuenta.rol && permisos.length > 0 && <label className="role-filter"><span>Tipo de permiso</span><select aria-label="Filtrar permisos por tipo" value={tipoPermiso} onChange={(evento) => setTipoPermiso(evento.target.value)}><option value="todos">Todos los tipos</option>{tiposPermiso.map((tipo) => <option key={tipo} value={tipo}>{tipo === 'medico' ? 'Médico' : tipo === 'paciente' ? 'Paciente' : tipo}</option>)}</select></label>}</div>
      {!cuenta.rol || permisos.length === 0 ? <p className="empty-permissions">No hay permisos para mostrar.</p> : permisosVisibles.length ? <ul className="detail-permission-list">{permisosVisibles.map((permiso) => <li key={permiso}><span>{CAMPOS_PERMISO[permiso] || permiso}</span><code>{permiso}</code></li>)}</ul> : <p className="empty-permissions">No hay permisos de este tipo.</p>}
    </article>
    <div className="account-form-actions"><button className="secondary-button" onClick={() => navegar(rutaLista)}>Volver a la lista</button><button className="primary-button" onClick={() => navegar(`/admin/cuentas/${cuenta.id}/editar${urlRuta.search}`)}>Editar cuenta</button></div>
  </section>;
}
