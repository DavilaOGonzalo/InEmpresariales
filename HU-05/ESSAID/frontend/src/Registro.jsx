import React, { useState } from 'react';

export default function Registro() {
  const [datos, setDatos] = useState({
    nombre: '', apellido: '', dni: '', correo: '', telefono: '', contrasena: '', confirmarContrasena: '',
  });
  const [mensaje, setMensaje] = useState('');
  const [enviando, setEnviando] = useState(false);

  function actualizarCampo(evento) {
    const { name, value } = evento.target;
    setDatos((actuales) => ({ ...actuales, [name]: value }));
    setMensaje('');
  }

  async function enviarFormulario(evento) {
    evento.preventDefault();
    if (datos.contrasena !== datos.confirmarContrasena) {
      setMensaje('Las contrasenas no coinciden.');
      return;
    }

    setEnviando(true);
    setMensaje('');
    try {
      const respuesta = await fetch('/api/registro/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre: datos.nombre,
          apellido: datos.apellido,
          dni: datos.dni,
          correo: datos.correo,
          telefono: datos.telefono,
          contrasena: datos.contrasena,
        }),
      });
      const cuerpo = await respuesta.text();
      let resultado = {};
      if (cuerpo) {
        try {
          resultado = JSON.parse(cuerpo);
        } catch {
          throw new Error(`Django respondio algo que no es JSON (HTTP ${respuesta.status}). Revisa la terminal de Django.`);
        }
      }
      if (!respuesta.ok) throw new Error(resultado.error || `Django respondio con error HTTP ${respuesta.status}.`);
      if (!cuerpo) throw new Error(`Django respondio vacio (HTTP ${respuesta.status}). Revisa la vista de registro.`);
      setMensaje(resultado.mensaje);
      setDatos({ nombre: '', apellido: '', dni: '', correo: '', telefono: '', contrasena: '', confirmarContrasena: '' });
    } catch (error) {
      setMensaje(error.message || 'No se pudo conectar con Django. Comprueba que este encendido.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="registro-page">
      <section className="registro-card" aria-labelledby="titulo-registro">
        <div className="registro-marca">
          <span className="registro-icono" aria-hidden="true">+</span>
          <span>ESSAID</span>
        </div>
        <h1 id="titulo-registro">Crear una cuenta</h1>
        <p className="registro-intro">Completa tus datos para registrarte.</p>

        <form className="registro-formulario" onSubmit={enviarFormulario}>
          <div className="campo">
            <label htmlFor="nombre">Nombre</label>
            <input id="nombre" name="nombre" placeholder="Tu nombre" value={datos.nombre} onChange={actualizarCampo} autoComplete="given-name" required />
          </div>
          <div className="campo">
            <label htmlFor="apellido">Apellido</label>
            <input id="apellido" name="apellido" placeholder="Tu apellido" value={datos.apellido} onChange={actualizarCampo} autoComplete="family-name" required />
          </div>
          <div className="campo campo-completo">
            <label htmlFor="dni">DNI</label>
            <input id="dni" name="dni" type="text" inputMode="numeric" pattern="[0-9]{8}" minLength={8} maxLength={8} title="El DNI debe tener exactamente 8 digitos." placeholder="8 digitos" value={datos.dni} onChange={actualizarCampo} autoComplete="off" required />
          </div>
          <div className="campo campo-completo">
            <label htmlFor="correo">Correo</label>
            <input id="correo" name="correo" type="email" pattern="[^@\s]+@(tecsup\.edu\.pe|gmail\.com)" title="Usa un correo @tecsup.edu.pe o @gmail.com." placeholder="nombre@gmail.com" value={datos.correo} onChange={actualizarCampo} autoComplete="email" required />
          </div>
          <div className="campo campo-completo">
            <label htmlFor="telefono">Telefono</label>
            <input id="telefono" name="telefono" type="tel" inputMode="numeric" pattern="[0-9]{9}" minLength={9} maxLength={9} title="El telefono debe tener exactamente 9 digitos." placeholder="9 digitos" value={datos.telefono} onChange={actualizarCampo} autoComplete="tel" required />
          </div>
          <div className="campo campo-completo">
            <label htmlFor="contrasena">Contrasena</label>
            <input id="contrasena" name="contrasena" type="password" placeholder="Crea una contrasena" value={datos.contrasena} onChange={actualizarCampo} autoComplete="new-password" required />
          </div>
          <div className="campo campo-completo">
            <label htmlFor="confirmarContrasena">Confirmar contrasena</label>
            <input id="confirmarContrasena" name="confirmarContrasena" type="password" placeholder="Escribela otra vez" value={datos.confirmarContrasena} onChange={actualizarCampo} autoComplete="new-password" required />
          </div>
          <button className="registro-boton" type="submit" disabled={enviando}>
            {enviando ? 'Creando cuenta...' : 'Crear cuenta'}
          </button>
          {mensaje && <p className="registro-mensaje" role="status">{mensaje}</p>}
        </form>
      </section>
    </main>
  );
}
