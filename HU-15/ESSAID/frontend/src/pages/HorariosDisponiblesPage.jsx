import { useState } from 'react';
import { api } from '../api.js';

function fechaLocal() {
  const ahora = new Date();
  const ajustar = (valor) => String(valor).padStart(2, '0');
  return `${ahora.getFullYear()}-${ajustar(ahora.getMonth() + 1)}-${ajustar(ahora.getDate())}`;
}

export default function HorariosDisponiblesPage() {
  const [fecha, setFecha] = useState(fechaLocal());
  const [horarios, setHorarios] = useState([]);
  const [consultado, setConsultado] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');

  async function consultar(evento) {
    evento.preventDefault();
    setCargando(true);
    setConsultado(true);
    setError('');
    try {
      const consulta = new URLSearchParams({ fecha });
      const resultado = await api(`/api/horarios-disponibles/?${consulta.toString()}`);
      setHorarios(resultado.horarios);
    } catch (fallo) {
      setHorarios([]);
      setError(fallo.message);
    } finally {
      setCargando(false);
    }
  }

  const porMedico = horarios.reduce((grupos, horario) => {
    const clave = `${horario.medico_id}`;
    if (!grupos[clave]) grupos[clave] = { ...horario, horas: [] };
    grupos[clave].horas.push(horario.hora);
    return grupos;
  }, {});

  return (
    <main className="public-schedule-page">
      <header className="public-schedule-header">
        <a className="admin-brand" href="/admin/login"><span className="admin-brand-mark">+</span><span>ESSAID</span></a>
        <span>Disponibilidad para pacientes</span>
      </header>
      <section className="public-schedule-content">
        <p className="eyebrow">AGENDA MÉDICA</p>
        <h1>Encuentra un horario disponible</h1>
        <p className="heading-copy">Elige una fecha para ver únicamente los espacios libres por médico.</p>
        <form className="appointment-filter-card public-schedule-search" onSubmit={consultar}>
          <label htmlFor="fecha-disponible">Fecha de atención</label>
          <input id="fecha-disponible" type="date" min={fechaLocal()} value={fecha} onChange={(evento) => setFecha(evento.target.value)} required />
          <button className="primary-button" type="submit" disabled={cargando}>{cargando ? 'Buscando…' : 'Buscar horarios'}</button>
        </form>
        {error && <p className="form-error" role="alert">No se pudieron consultar los horarios: {error}</p>}
        {consultado && !cargando && !error && horarios.length === 0 && <div className="public-schedule-empty">No hay horarios disponibles para esta fecha. Prueba con otro día.</div>}
        <div className="public-schedule-grid">
          {Object.values(porMedico).map((grupo) => (
            <article className="public-schedule-card" key={grupo.medico_id}>
              <div className="public-doctor-icon" aria-hidden="true">＋</div>
              <div className="public-doctor-heading"><h2>{grupo.medico}</h2><p>{grupo.especialidad || 'Atención médica'}</p></div>
              <p className="public-slot-label">HORARIOS LIBRES</p>
              <div className="public-slot-list">{grupo.horas.map((hora) => <span className="public-slot" key={hora}>{hora}</span>)}</div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
