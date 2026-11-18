import React from 'react';

export default function AdminLayout({ administrador, ruta, navegar, onLogout, children }) {
  const editar = ruta.includes('/editar');
  const crear = ruta.endsWith('/nueva');
  const titulo = editar ? 'Editar cuenta' : crear ? 'Crear cuenta' : 'Cuentas';

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="admin-brand"><span className="admin-brand-mark">+</span><span>ESSAID</span></div>
        <p className="nav-caption">ADMINISTRACION</p>
        <button className={`nav-item ${ruta.startsWith('/admin/cuentas') ? 'active' : ''}`} onClick={() => navegar('/admin/cuentas')}><span>▦</span> Cuentas de usuario</button>
        <div className="sidebar-bottom"><div className="admin-avatar">AD</div><div><strong>Superusuario</strong><small>{administrador}</small></div><button className="logout-button" onClick={onLogout} aria-label="Cerrar sesion" title="Cerrar sesion"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 17l5-5-5-5M15 12H3M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7" /></svg></button></div>
      </aside>
      <main className="admin-main">
        <header className="admin-topbar"><div><span className="topbar-label">ESSAID</span><span className="crumb-separator">/</span><strong>{titulo}</strong></div><span className="preview-pill private-pill">SESION SEGURA</span></header>
        {children}
      </main>
    </div>
  );
}
