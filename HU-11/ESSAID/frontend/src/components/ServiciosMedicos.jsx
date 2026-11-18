import React from 'react';

export default function ServiciosMedicos({ servicios, navegar, mensaje }) {
  return (
    <section className="admin-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">GESTION DE SERVICIOS</p>
          <h1>Servicios medicos</h1>
          <p className="heading-copy">Administra los servicios ofrecidos por cada hospital.</p>
        </div>
        <button className="primary-button add-button" onClick={() => navegar('/admin/servicios/nuevo')}>
          <span>＋</span> Registrar servicio
        </button>
      </div>
      {mensaje && <p className="success-message" role="status" aria-live="polite">{mensaje}</p>}
      <section className="table-card">
        <div className="table-heading">
          <div><h2>Servicios registrados</h2><p>{servicios.length} servicios medicos en el sistema.</p></div>
        </div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>SERVICIO</th><th>HOSPITAL</th><th>DESCRIPCION</th><th>ACCIONES</th></tr></thead>
            <tbody>
              {servicios.map((servicio) => (
                <tr key={servicio.id}>
                  <td><strong>{servicio.nombre}</strong></td>
                  <td>{servicio.hospital_nombre}</td>
                  <td>{servicio.descripcion || 'Sin descripcion'}</td>
                  <td><div className="row-actions"><button onClick={() => navegar(`/admin/servicios/${servicio.id}/editar`)}>Editar</button></div></td>
                </tr>
              ))}
              {servicios.length === 0 && <tr><td className="empty-row" colSpan="4">Todavia no hay servicios medicos registrados.</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="table-footer">Mostrando {servicios.length} servicios medicos</div>
      </section>
    </section>
  );
}