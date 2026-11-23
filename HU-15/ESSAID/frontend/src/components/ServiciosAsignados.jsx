import React from 'react';

export default function ServiciosAsignados({ asignaciones, navegar, mensaje }) {
  return (
    <section className="admin-content">
      <div className="page-heading">
        <div><p className="eyebrow">SERVICIOS POR HOSPITAL</p><h1>Asignaciones</h1><p className="heading-copy">Servicios del catalogo asociados a cada hospital.</p></div>
        <button className="primary-button add-button" onClick={() => navegar('/admin/servicios/asignar')}>Asignar servicio</button>
      </div>
      {mensaje && <p className="success-message" role="status" aria-live="polite">{mensaje}</p>}
      <section className="table-card">
        <div className="table-heading"><div><h2>Servicios asignados</h2><p>{asignaciones.length} asignaciones registradas.</p></div></div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>HOSPITAL</th><th>CODIGO</th><th>SERVICIO</th><th>DESCRIPCION</th><th>DISPONIBILIDAD</th></tr></thead>
            <tbody>
              {asignaciones.map((item) => {
                const disponible = item.hospital_activo && item.servicio_activo;
                return <tr key={item.id}><td>{item.hospital_nombre}</td><td>Servicio {item.servicio_numero}</td><td><strong>{item.servicio_nombre}</strong></td><td>{item.descripcion || 'Sin descripcion'}</td><td><span className={`status-badge ${disponible ? '' : 'inactive-badge'}`}><i />{disponible ? 'Disponible' : 'No disponible'}</span></td></tr>;
              })}
              {asignaciones.length === 0 && <tr><td className="empty-row" colSpan="5">Todavia no hay servicios asignados.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
      <div className="account-form-actions"><button className="secondary-button" onClick={() => navegar('/admin/servicios')}>Volver al catalogo</button></div>
    </section>
  );
}
