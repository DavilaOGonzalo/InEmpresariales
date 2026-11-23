import React from 'react';

export default function ServicioDetalle({ servicio, asignaciones, navegar }) {
  const hospitales = asignaciones.filter((item) => item.servicio_id === servicio.id);

  return (
    <section className="admin-content account-form-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">CATALOGO DE SERVICIOS</p>
          <h1>{servicio.nombre}</h1>
          <p className="heading-copy">Detalle completo del servicio medico.</p>
        </div>
        <div className="page-actions">
          <button className="secondary-button" onClick={() => navegar(`/admin/servicios/${servicio.id}/editar`)}>Editar</button>
        </div>
      </div>
      <section className="account-form-card doctor-detail service-detail">
        <dl>
          <div><dt>Codigo</dt><dd>Servicio {servicio.numero}</dd></div>
          <div><dt>Nombre</dt><dd>{servicio.nombre}</dd></div>
          <div><dt>Estado</dt><dd><span className={`status-badge ${servicio.activo ? '' : 'inactive-badge'}`}><i />{servicio.activo ? 'Activo' : 'Inactivo'}</span></dd></div>
          <div className="service-full-description"><dt>Descripcion</dt><dd>{servicio.descripcion || 'Sin descripcion registrada.'}</dd></div>
          <div><dt>Hospitales asignados</dt><dd>{hospitales.length ? hospitales.map((item) => item.hospital_nombre).join(', ') : 'Ninguno'}</dd></div>
        </dl>
        <div className="account-form-actions">
          <button className="secondary-button" onClick={() => navegar('/admin/servicios')}>Volver al catalogo</button>
        </div>
      </section>
    </section>
  );
}
