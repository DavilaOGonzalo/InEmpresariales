import React, { useMemo, useState } from 'react';

export default function Cuentas({ cuentas, navegar, onDelete, onToggleStatus, procesando }) {
  const [busqueda, setBusqueda] = useState('');
  const visibles = useMemo(() => cuentas.filter((cuenta) =>
    `${cuenta.nombre} ${cuenta.apellido} ${cuenta.dni} ${cuenta.correo} ${cuenta.rol}`.toLowerCase().includes(busqueda.toLowerCase()),
  ), [cuentas, busqueda]);

  return (
    <section className="admin-content">
      <div className="page-heading"><div><p className="eyebrow">GESTION DE ACCESOS</p><h1>Cuentas de usuario</h1><p className="heading-copy">Administra quien puede acceder al sistema.</p></div><button className="primary-button add-button" onClick={() => navegar('/admin/cuentas/nueva')}><span>＋</span> Crear cuenta</button></div>
      <div className="stat-grid">
        <article className="stat-card"><span className="stat-icon teal">♙</span><div><small>Total de cuentas</small><strong>{cuentas.length}</strong></div></article>
        <article className="stat-card"><span className="stat-icon green">✓</span><div><small>Cuentas activas</small><strong>{cuentas.filter((cuenta) => cuenta.estado === 'Activa').length}</strong></div></article>
        <article className="stat-card"><span className="stat-icon blue">＋</span><div><small>Altas recientes</small><strong>{Math.min(cuentas.length, 3)}</strong></div></article>
      </div>
      <section className="table-card">
        <div className="table-heading"><div><h2>Usuarios registrados</h2><p>Consulta y modifica las cuentas del sistema.</p></div><label className="search-box"><span>⌕</span><input aria-label="Buscar cuenta" value={busqueda} onChange={(evento) => setBusqueda(evento.target.value)} placeholder="Buscar por nombre, DNI o correo" /></label></div>
        <div className="table-scroll"><table><thead><tr><th>USUARIO</th><th>DNI</th><th>TELEFONO</th><th>ESTADO</th><th></th></tr></thead><tbody>
          {visibles.map((cuenta) => <tr key={cuenta.id}><td><div className="user-cell"><span className="user-avatar">{`${cuenta.nombre} ${cuenta.apellido}`.split(' ').map((parte) => parte[0]).slice(0, 2).join('')}</span><span><strong>{cuenta.nombre} {cuenta.apellido}</strong><small>{cuenta.correo}</small><small>Rol: {cuenta.rol_nombre}{cuenta.protegida ? ' · Cuenta protegida' : ''}</small></span></div></td><td>{cuenta.dni}</td><td>{cuenta.telefono}</td><td><span className={`status-badge ${cuenta.estado === 'Activa' ? '' : 'inactive-badge'}`}><i />{cuenta.estado}</span></td><td><div className="row-actions"><button disabled={cuenta.protegida} title={cuenta.protegida ? 'Esta cuenta está protegida' : ''} onClick={() => navegar(`/admin/cuentas/${cuenta.id}/editar`)}>Editar</button><button disabled={procesando || cuenta.protegida || !cuenta.tiene_cuenta} title={cuenta.protegida ? 'Esta cuenta está protegida' : !cuenta.tiene_cuenta ? 'El perfil no tiene una cuenta de acceso asociada' : ''} onClick={() => onToggleStatus(cuenta)}>{cuenta.estado === 'Activa' ? 'Desactivar' : 'Activar'}</button><button className="delete-action" disabled={procesando || cuenta.protegida} title={cuenta.protegida ? 'Esta cuenta está protegida' : ''} onClick={() => onDelete(cuenta)}>Eliminar</button></div></td></tr>)}
          {visibles.length === 0 && <tr><td className="empty-row" colSpan="5">{cuentas.length ? 'No hay cuentas que coincidan con la busqueda.' : 'Todavia no hay cuentas registradas.'}</td></tr>}
        </tbody></table></div>
        <div className="table-footer">Mostrando {visibles.length} de {cuentas.length} cuentas</div>
      </section>
      <p className="preview-banner secure-banner"><span>✓</span> Las cuentas se consultan y guardan en la base de datos de Django.</p>
    </section>
  );
}
