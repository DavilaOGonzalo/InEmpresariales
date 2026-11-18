import React from 'react';

export default function HospitalDetalle({ hospital, navegar, mensaje = '' }) {
  return (
    <section className="admin-content account-form-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">GESTION DE HOSPITALES</p>
          <h1>{hospital.nombre}</h1>
          <p className="heading-copy">Informacion registrada del hospital seleccionado.</p>
        </div>
        <button className="primary-button add-button" onClick={() => navegar(`/admin/hospitales/${hospital.id}/editar`)}>Editar hospital</button>
      </div>
      {mensaje && <p className="success-message" role="status">{mensaje}</p>}
      <section className="account-form-card doctor-detail">
        <dl>
          <div><dt>Nombre</dt><dd>{hospital.nombre}</dd></div>
          <div><dt>Direccion</dt><dd>{hospital.direccion}</dd></div>
          <div><dt>Contacto</dt><dd>{hospital.contacto}</dd></div>
        </dl>
        <div className="account-form-actions">
          <button className="secondary-button" onClick={() => navegar('/admin/hospitales')}>Volver a hospitales</button>
        </div>
      </section>
    </section>
  );
}