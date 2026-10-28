import React, { useState } from 'react';

export default function LoginAdmin({ onLogin, error, procesando }) {
  const [usuario, setUsuario] = useState('');
  const [contrasena, setContrasena] = useState('');

  function enviar(evento) {
    evento.preventDefault();
    onLogin({ usuario, contrasena });
  }

  return (
    <main className="admin-login-page">
      <section className="admin-login-card">
        <div className="admin-brand"><span className="admin-brand-mark">+</span><span>ESSAID</span></div>
        <p className="eyebrow">ACCESO ADMINISTRATIVO</p>
        <h1>Bienvenido</h1>
        <p className="login-copy">Inicia sesion para administrar las cuentas del sistema.</p>
        <form className="login-form" onSubmit={enviar}>
          <div className="login-field"><label htmlFor="admin-user">Usuario o correo</label><input id="admin-user" value={usuario} onChange={(evento) => setUsuario(evento.target.value)} autoComplete="username" placeholder="Tu usuario de administrador" required /></div>
          <div className="login-field"><label htmlFor="admin-password">Contrasena</label><input id="admin-password" type="password" value={contrasena} onChange={(evento) => setContrasena(evento.target.value)} autoComplete="current-password" placeholder="Tu contrasena" required /></div>
          <button className="primary-button" type="submit" disabled={procesando}>{procesando ? 'Verificando...' : 'Iniciar sesion'}</button>
          {error && <p className="form-error" role="alert">{error}</p>}
        </form>
        <p className="preview-note">Solo pueden entrar cuentas de Django marcadas como superusuario.</p>
      </section>
    </main>
  );
}
