import React from 'react';

export default function Hospitales({ hospitales, navegar, mensaje, onToggleStatus, procesando, errorCarga }) {
  return (
    <section className="admin-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">GESTION DE HOSPITALES</p>
          <h1>Hospitales</h1>
          <p className="heading-copy">Consulta los hospitales registrados en el sistema.</p>
        </div>
        <button className="primary-button add-button" onClick={() => navegar('/admin/hospitales/nuevo')}>
          <span>＋</span> Registrar hospital
        </button>
      </div>
      {mensaje && <p className="success-message" role="status" aria-live="polite">{mensaje}</p>}
      {errorCarga && <p className="form-error" role="alert">No se pudieron cargar los hospitales: {errorCarga}</p>}
      <section className="table-card">
        <div className="table-heading">
          <div><h2>Hospitales registrados</h2><p>{hospitales.length} hospitales en el sistema.</p></div>
        </div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>NOMBRE</th><th>DIRECCION</th><th>CONTACTO</th><th>ESTADO</th><th>ACCIONES</th></tr></thead>
            <tbody>
              {hospitales.map((hospital) => (
                <tr key={hospital.id}>
                  <td><strong>{hospital.nombre}</strong></td>
                  <td>{hospital.direccion}</td>
                  <td>{hospital.contacto}</td>
                  <td><span className={`status-badge ${hospital.activo ? '' : 'inactive-badge'}`}><i />{hospital.activo ? 'Activo' : 'Inactivo'}</span></td>
                  <td><div className="row-actions"><button onClick={() => navegar(`/admin/hospitales/${hospital.id}`)}>Ver</button><button onClick={() => navegar(`/admin/hospitales/${hospital.id}/editar`)}>Editar</button><button disabled={procesando} onClick={() => onToggleStatus(hospital)}>{hospital.activo ? 'Desactivar' : 'Activar'}</button></div></td>
                </tr>
              ))}
              {hospitales.length === 0 && <tr><td className="empty-row" colSpan="5">{errorCarga ? 'No se pudieron mostrar los hospitales.' : 'No hay hospitales registrados en la base de datos.'}</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="table-footer">Mostrando {hospitales.length} hospitales, activos e inactivos</div>
      </section>
    </section>
  );
}
