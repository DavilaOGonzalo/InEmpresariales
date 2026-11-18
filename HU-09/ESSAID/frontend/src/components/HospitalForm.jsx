import React, { useState } from 'react';

const CAMPOS = [
  { name: 'nombre', label: 'Nombre del hospital', maxLength: 150 },
  { name: 'direccion', label: 'Direccion', maxLength: 255 },
  { name: 'contacto', label: 'Contacto', maxLength: 100 },
];

export default function HospitalForm({ onSave, onCancel, error, procesando }) {
  const [datos, setDatos] = useState({ nombre: '', direccion: '', contacto: '' });

  function actualizar(evento) {
    setDatos((actuales) => ({ ...actuales, [evento.target.name]: evento.target.value }));
  }

  function enviar(evento) {
    evento.preventDefault();
    onSave(Object.fromEntries(Object.entries(datos).map(([clave, valor]) => [clave, valor.trim()])));
  }

  return (
    <section className="admin-content account-form-page">
      <div className="page-heading">
        <div><p className="eyebrow">GESTION DE HOSPITALES</p><h1>Registrar hospital</h1><p className="heading-copy">Completa los datos para agregarlo al sistema.</p></div>
      </div>
      <form className="account-form-card" onSubmit={enviar}>
        <div className="account-form-grid">
          {CAMPOS.map((campo) => (
            <label key={campo.name}>
              {campo.label}
              <input
                name={campo.name}
                value={datos[campo.name]}
                onChange={actualizar}
                maxLength={campo.maxLength}
                required
                aria-invalid={Boolean(error)}
              />
            </label>
          ))}
        </div>
        {error && <p className="form-error" role="alert">{error}</p>}
        <div className="account-form-actions">
          <button className="secondary-button" type="button" onClick={onCancel} disabled={procesando}>Cancelar</button>
          <button className="primary-button" type="submit" disabled={procesando}>{procesando ? 'Guardando...' : 'Guardar hospital'}</button>
        </div>
      </form>
    </section>
  );
}
