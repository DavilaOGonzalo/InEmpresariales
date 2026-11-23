import React from 'react';

export default function ServiciosMedicos({ servicios, asignaciones, navegar, mensaje, onToggleStatus, procesando, errorCarga }) {
  return (
    <section className="admin-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">CATALOGO DE SERVICIOS</p>
          <h1>Servicios medicos</h1>
          <p className="heading-copy">Administra el catalogo y asigna sus servicios a hospitales.</p>
        </div>
        <div className="page-actions">
          <button className="secondary-button" onClick={() => navegar('/admin/servicios/asignados')}>Ver asignaciones</button>
          <button className="primary-button add-button" onClick={() => navegar('/admin/servicios/nuevo')}><span>＋</span> Nuevo servicio</button>
        </div>
      </div>
      {mensaje && <p className="success-message" role="status" aria-live="polite">{mensaje}</p>}
      {errorCarga && <p className="form-error" role="alert">No se pudieron cargar los servicios: {errorCarga}</p>}
      <section className="table-card">
        <div className="table-heading">
          <div><h2>Catalogo disponible</h2><p>{servicios.length} servicios en el catalogo.</p></div>
        </div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>CODIGO</th><th>SERVICIO</th><th>DESCRIPCION</th><th>HOSPITALES</th><th>ESTADO</th><th>ACCIONES</th></tr></thead>
            <tbody>
              {servicios.map((servicio) => {
                const totalAsignaciones = asignaciones.filter((item) => item.servicio_id === servicio.id).length;
                return (
                  <tr key={servicio.id}>
                    <td>Servicio {servicio.numero}</td>
                    <td><strong>{servicio.nombre}</strong></td>
                    <td className="service-description-cell">
                      <p title={servicio.descripcion || 'Sin descripcion'}>{servicio.descripcion || 'Sin descripcion'}</p>
                    </td>
                    <td>{totalAsignaciones}</td>
                    <td><span className={`status-badge ${servicio.activo ? '' : 'inactive-badge'}`}><i />{servicio.activo ? 'Activo' : 'Inactivo'}</span></td>
                    <td><div className="row-actions"><button onClick={() => navegar(`/admin/servicios/${servicio.id}`)}>Ver</button><button onClick={() => navegar(`/admin/servicios/${servicio.id}/editar`)}>Editar</button><button disabled={!servicio.activo || procesando} onClick={() => navegar(`/admin/servicios/asignar?servicio=${servicio.id}`)}>Asignar</button><button disabled={procesando} onClick={() => onToggleStatus(servicio)}>{servicio.activo ? 'Desactivar' : 'Activar'}</button></div></td>
                  </tr>
                );
              })}
              {servicios.length === 0 && <tr><td className="empty-row" colSpan="6">{errorCarga ? 'No se pudieron mostrar los servicios.' : 'No hay servicios registrados en la base de datos.'}</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}
