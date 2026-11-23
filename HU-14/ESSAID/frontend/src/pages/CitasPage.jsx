import { useState } from 'react';

const ESTADOS_CITA = [
  ['programada', 'Programada'],
  ['confirmada', 'Confirmada'],
  ['completada', 'Completada'],
  ['cancelada', 'Cancelada'],
];

function iniciales(nombre) {
  return nombre.split(/\s+/).filter(Boolean).slice(0, 2).map((parte) => parte[0]).join('').toUpperCase();
}

function fechaVisible(fecha) {
  const [anio, mes, dia] = fecha.split('-');
  return `${dia}/${mes}/${anio}`;
}

export default function CitasPage({ citas, totalCitas, cargando, error, mensaje, onBuscar, onCambiarEstado }) {
  const [filtros, setFiltros] = useState({ fecha: '', medico: '', estado: '' });
  const [estadosSeleccionados, setEstadosSeleccionados] = useState({});
  const [guardandoId, setGuardandoId] = useState(null);
  const [errorEstado, setErrorEstado] = useState('');

  const transiciones = {
    programada: ['confirmada', 'cancelada'],
    confirmada: ['completada', 'cancelada'],
    completada: [],
    cancelada: [],
  };

  async function guardarEstado(cita) {
    const nuevoEstado = estadosSeleccionados[cita.id];
    if (!nuevoEstado || !transiciones[cita.estado]?.includes(nuevoEstado)) return;
    setGuardandoId(cita.id);
    setErrorEstado('');
    try {
      await onCambiarEstado(cita.id, nuevoEstado);
      setEstadosSeleccionados((actuales) => {
        const nuevos = { ...actuales };
        delete nuevos[cita.id];
        return nuevos;
      });
    } catch (fallo) {
      setErrorEstado(fallo.message);
    } finally {
      setGuardandoId(null);
    }
  }

  function actualizar(evento) {
    setFiltros((actuales) => ({ ...actuales, [evento.target.name]: evento.target.value }));
  }

  function enviar(evento) {
    evento.preventDefault();
    onBuscar(filtros);
  }

  function limpiar() {
    const vacios = { fecha: '', medico: '', estado: '' };
    setFiltros(vacios);
    onBuscar(vacios);
  }

  return (
    <section className="admin-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">AGENDA</p>
          <h1>Citas médicas</h1>
          <p className="heading-copy">Consulta las citas registradas y filtra la agenda por fecha, médico o estado.</p>
        </div>
      </div>

      <div className="stat-grid cita-stat-grid">
        <article className="stat-card"><span className="stat-icon teal">▣</span><div><small>Citas registradas</small><strong>{totalCitas}</strong></div></article>
        <article className="stat-card"><span className="stat-icon blue">⌕</span><div><small>Resultados actuales</small><strong>{citas.length}</strong></div></article>
      </div>

      <form className="appointment-filter-card" onSubmit={enviar}>
        <div className="appointment-filter-heading"><div><h2>Buscar citas</h2><p>Combina uno o más filtros para encontrar una cita.</p></div></div>
        <div className="appointment-filter-fields">
          <label htmlFor="cita-fecha">Fecha<input id="cita-fecha" name="fecha" type="date" value={filtros.fecha} onChange={actualizar} /></label>
          <label htmlFor="cita-medico">Médico<input id="cita-medico" name="medico" type="search" value={filtros.medico} onChange={actualizar} placeholder="Nombre del médico" /></label>
          <label htmlFor="cita-estado">Estado<select id="cita-estado" name="estado" value={filtros.estado} onChange={actualizar}><option value="">Todos los estados</option>{ESTADOS_CITA.map(([valor, etiqueta]) => <option key={valor} value={valor}>{etiqueta}</option>)}</select></label>
        </div>
        <div className="appointment-filter-actions">
          <button className="secondary-button" type="button" onClick={limpiar} disabled={cargando}>Limpiar filtros</button>
          <button className="primary-button" type="submit" disabled={cargando}>{cargando ? 'Buscando...' : 'Buscar citas'}</button>
        </div>
      </form>

      {error && <p className="form-error" role="alert">No se pudieron cargar las citas: {error}</p>}
      {mensaje && <p className="form-success" role="status">{mensaje}</p>}
      {errorEstado && <p className="form-error" role="alert">No se pudo actualizar el estado: {errorEstado}</p>}

      <section className="table-card appointment-table-card">
        <div className="table-heading"><div><h2>Listado de citas</h2><p>{citas.length} {citas.length === 1 ? 'resultado' : 'resultados'}</p></div></div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>PACIENTE</th><th>MÉDICO</th><th>FECHA</th><th>HORA</th><th>ESTADO</th><th>ACCIONES</th></tr></thead>
            <tbody>
              {citas.map((cita) => (
                <tr key={cita.id}>
                  <td><div className="user-cell"><span className="user-avatar">{iniciales(cita.paciente)}</span><strong>{cita.paciente}</strong></div></td>
                  <td>{cita.medico}</td>
                  <td>{fechaVisible(cita.fecha)}</td>
                  <td>{cita.hora.slice(0, 5)}</td>
                  <td><span className={`appointment-status appointment-status-${cita.estado}`}>{cita.estado_nombre}</span></td>
                  <td>
                    {transiciones[cita.estado]?.length ? <div className="appointment-status-actions">
                      <select aria-label={`Nuevo estado para la cita de ${cita.paciente}`} value={estadosSeleccionados[cita.id] || ''} onChange={(evento) => setEstadosSeleccionados((actuales) => ({ ...actuales, [cita.id]: evento.target.value }))}>
                        <option value="">Cambiar estado...</option>
                        {transiciones[cita.estado].map((valor) => <option key={valor} value={valor}>{ESTADOS_CITA.find(([estado]) => estado === valor)?.[1]}</option>)}
                      </select>
                      <button className="secondary-button" type="button" disabled={!estadosSeleccionados[cita.id] || guardandoId === cita.id} onClick={() => guardarEstado(cita)}>{guardandoId === cita.id ? 'Guardando...' : 'Guardar'}</button>
                    </div> : <span className="muted-copy">Estado final</span>}
                  </td>
                </tr>
              ))}
              {citas.length === 0 && <tr><td className="empty-row" colSpan="6">{cargando ? 'Cargando citas...' : error ? 'No se pudieron mostrar los resultados.' : 'No hay citas que coincidan con la búsqueda.'}</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}
