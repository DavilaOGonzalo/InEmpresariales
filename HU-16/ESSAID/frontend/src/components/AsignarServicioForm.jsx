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
              {servicios.filter((servicio) => servicio.activo).map((servicio) => <option key={servicio.id} value={servicio.id}>Servicio {servicio.numero} · {servicio.nombre}</option>)}
            </select>
          </label>
          <label>
            Hospital
            <select name="hospital_id" value={datos.hospital_id} onChange={actualizar} required>
              <option value="">Selecciona un hospital</option>
              {hospitales.filter((hospital) => hospital.activo).map((hospital) => <option key={hospital.id} value={hospital.id}>{hospital.nombre}</option>)}
            </select>
          </label>
        </div>
        {error && <p className="form-error" role="alert">{error}</p>}
        {hospitales.every((hospital) => !hospital.activo) && <p className="form-error" role="status">No hay hospitales activos disponibles para asignar.</p>}
        {servicios.every((servicio) => !servicio.activo) && <p className="form-error" role="status">No hay servicios activos disponibles para asignar.</p>}
        <div className="account-form-actions">
          <button className="secondary-button" type="button" onClick={onCancel} disabled={procesando}>Volver a servicios</button>
          <button className="primary-button" type="submit" disabled={procesando || hospitales.every((hospital) => !hospital.activo) || servicios.every((servicio) => !servicio.activo)}>{procesando ? 'Guardando...' : 'Asignar servicio'}</button>
        </div>
      </form>
    </section>
  );
}
