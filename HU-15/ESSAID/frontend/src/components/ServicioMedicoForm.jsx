import React, { useState } from 'react';

export default function ServicioMedicoForm({ servicio, onSave, onCancel, error, procesando }) {
  const [datos, setDatos] = useState({
    nombre: servicio?.nombre || '',
    descripcion: servicio?.descripcion || '',
  });

  function actualizar(evento) {
    setDatos((actuales) => ({ ...actuales, [evento.target.name]: evento.target.value }));
  }

  function enviar(evento) {
    evento.preventDefault();
    onSave({ nombre: datos.nombre.trim(), descripcion: datos.descripcion.trim() });
  }

  return (
    <section className="admin-content account-form-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">CATALOGO DE SERVICIOS</p>
          <h1>{servicio ? 'Editar servicio' : 'Nuevo servicio'}</h1>
          <p className="heading-copy">{servicio ? `Servicio ${servicio.numero} · ${servicio.nombre}` : 'Agrega un servicio al catalogo para poder asignarlo a hospitales.'}</p>
        </div>
      </div>
      <form className="account-form-card" onSubmit={enviar}>
        <div className="account-form-grid">
          <label>
            Nombre del servicio
            <input name="nombre" value={datos.nombre} onChange={actualizar} maxLength={150} required aria-invalid={Boolean(error)} />
          </label>
          <label className="service-description-field">
            Descripcion
            <textarea name="descripcion" value={datos.descripcion} onChange={actualizar} maxLength={1000} rows={4} />
          </label>
        </div>
        {error && <p className="form-error" role="alert">{error}</p>}
        <div className="account-form-actions">
          <button className="secondary-button" type="button" onClick={onCancel} disabled={procesando}>Volver al catalogo</button>
          <button className="primary-button" type="submit" disabled={procesando}>{procesando ? 'Guardando...' : servicio ? 'Guardar cambios' : 'Guardar servicio'}</button>
        </div>
      </form>
    </section>
  );
}