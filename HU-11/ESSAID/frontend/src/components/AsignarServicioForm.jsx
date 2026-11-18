import React, { useState } from 'react';

export default function AsignarServicioForm({ servicios, hospitales, servicioInicial, onSave, onCancel, error, procesando }) {
  const [datos, setDatos] = useState({ servicio_id: servicioInicial ? String(servicioInicial) : '', hospital_id: '' });

  function actualizar(evento) {
    setDatos((actuales) => ({ ...actuales, [evento.target.name]: evento.target.value }));
  }

  function enviar(evento) {
    evento.preventDefault();
    onSave({ servicio_id: Number(datos.servicio_id), hospital_id: Number(datos.hospital_id) });
  }

  return (
    <section className="admin-content account-form-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">ASIGNAR A HOSPITAL</p>
          <h1>Asignar servicio</h1>
          <p className="heading-copy">Elige un servicio del catalogo y el hospital que lo ofrecera.</p>
        </div>
      </div>
      <form className="account-form-card" onSubmit={enviar}>
        <div className="account-form-grid">
          <label>
            Servicio medico
            <select name="servicio_id" value={datos.servicio_id} onChange={actualizar} required>
              <option value="">Selecciona un servicio</option>
              {servicios.map((servicio) => <option key={servicio.id} value={servicio.id}>Servicio {servicio.numero} · {servicio.nombre}</option>)}
            </select>
          </label>
          <label>
            Hospital
            <select name="hospital_id" value={datos.hospital_id} onChange={actualizar} required>
              <option value="">Selecciona un hospital</option>
              {hospitales.map((hospital) => <option key={hospital.id} value={hospital.id}>{hospital.nombre}</option>)}
            </select>
          </label>
        </div>
        {error && <p className="form-error" role="alert">{error}</p>}
        {hospitales.length === 0 && <p className="form-error" role="status">Registra un hospital antes de asignar servicios.</p>}
        <div className="account-form-actions">
          <button className="secondary-button" type="button" onClick={onCancel} disabled={procesando}>Volver a servicios</button>
          <button className="primary-button" type="submit" disabled={procesando || hospitales.length === 0 || servicios.length === 0}>{procesando ? 'Guardando...' : 'Asignar servicio'}</button>
        </div>
      </form>
    </section>
  );
}