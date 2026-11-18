import React from 'react';

export default function AdminLayout({ administrador, ruta, navegar, onLogout, children }) {
  const editar = ruta.includes('/editar');
  const crear = ruta.endsWith('/nueva') || ruta.endsWith('/nuevo');
  const hospitales = ruta.startsWith('/admin/hospitales');
  const servicios = ruta.startsWith('/admin/servicios');
  const titulo = servicios ? (editar ? 'Editar servicio medico' : crear ? 'Registrar servicio medico' : 'Servicios medicos') : hospitales ? (ruta.endsWith('/editar') ? 'Editar hospital' : crear ? 'Registrar hospital' : 'Hospitales') : editar ? 'Editar cuenta' : crear ? 'Crear cuenta' : 'Cuentas';

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="admin-brand"><span className="admin-brand-mark">+</span><span>ESSAID</span></div>
        <p className="nav-caption">ADMINISTRACION</p>
        <button className={`nav-item ${ruta.startsWith('/admin/cuentas') ? 'active' : ''}`} onClick={() => navegar('/admin/cuentas')}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="8" r="3.5" /><path d="M3 20v-1.5a6 6 0 0 1 12 0V20M16 5.2a3.5 3.5 0 0 1 0 6.7M18 14a5 5 0 0 1 3 4.5V20" /></svg>
          Cuentas de usuario
        </button>
        <button className={`nav-item ${hospitales ? 'active' : ''}`} onClick={() => navegar('/admin/hospitales')}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 21V5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v16M2 21h20M9 21v-4h6v4M7 8h2m6 0h2M7 12h2m6 0h2" /><path d="M12 7v5m-2.5-2.5h5" /></svg>
          Hospitales
        </button>
        <button className={`nav-item ${servicios ? 'active' : ''}`} onClick={() => navegar('/admin/servicios')}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3h8a2 2 0 0 1 2 2v16H6V5a2 2 0 0 1 2-2Z" /><path d="M10 3V2h4v1m-2 5v8m-4-4h8" /></svg>
          Servicios medicos
        </button>
        <div className="sidebar-bottom"><div className="admin-avatar">AD</div><div><strong>Superusuario</strong><small>{administrador}</small></div><button className="logout-button" onClick={onLogout} aria-label="Cerrar sesion" title="Cerrar sesion"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 17l5-5-5-5M15 12H3M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7" /></svg></button></div>
      </aside>
      <main className="admin-main">
        <header className="admin-topbar"><div><span className="topbar-label">ESSAID</span><span className="crumb-separator">/</span><strong>{titulo}</strong></div><span className="preview-pill private-pill">SESION SEGURA</span></header>
        {children}
      </main>
    </div>
  );
}
