import React, { useEffect, useState } from 'react';
import { api } from '../api.js';

function fechaLocal() {
  const ahora = new Date();
  const ajustar = (valor) => String(valor).padStart(2, '0');
  return `${ahora.getFullYear()}-${ajustar(ahora.getMonth() + 1)}-${ajustar(ahora.getDate())}`;
}

const FORMULARIO_VACIO = {
  medico_id: '', fecha: fechaLocal(), hora_inicio: '09:00', hora_fin: '13:00', intervalo_minutos: '30',
};

export default function HorariosPage() {
  const [horarios, setHorarios] = useState([]);
  const [medicos, setMedicos] = useState([]);
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO);
  const [editarId, setEditarId] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');

  async function cargar() {
    setCargando(true);
    setError('');
    try {
      const resultado = await api('/api/admin/horarios/');
      setHorarios(resultado.horarios);
      setMedicos(resultado.medicos);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => { cargar(); }, []);

  function actualizar(evento) {
    setFormulario((actual) => ({ ...actual, [evento.target.name]: evento.target.value }));
  }

  function iniciarEdicion(horario) {
    setEditarId(horario.id);
    setMensaje('');
    setError('');
    setFormulario({
      medico_id: String(horario.medico_id),
      fecha: horario.fecha,
      hora_inicio: horario.hora_inicio,
      hora_fin: horario.hora_fin,
      intervalo_minutos: String(horario.intervalo_minutos),
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function cancelarEdicion() {
    setEditarId(null);
    setFormulario(FORMULARIO_VACIO);
    setError('');
  }

  async function guardar(evento) {
    evento.preventDefault();
    setGuardando(true);
    setError('');
    setMensaje('');
    const datos = {
      ...formulario,
      medico_id: Number(formulario.medico_id),
      intervalo_minutos: Number(formulario.intervalo_minutos),
    };
    try {
      const resultado = await api(editarId ? `/api/admin/horarios/${editarId}/` : '/api/admin/horarios/', {
        method: editarId ? 'PATCH' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos),
      });
      setMensaje(editarId
        ? `Se actualizaron los horarios de ${resultado.horario.medico}.`
        : `Se registró el horario de ${resultado.horario.medico}.`);
      setEditarId(null);
      setFormulario(FORMULARIO_VACIO);
      await cargar();
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setGuardando(false);
    }
  }

  async function cambiarActivo(horario) {
    setError('');
    setMensaje('');
    try {
      await api(`/api/admin/horarios/${horario.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activo: !horario.activo }),
      });
      setMensaje(`El horario de ${horario.medico} quedó ${horario.activo ? 'inactivo' : 'activo'}.`);
      await cargar();
    } catch (fallo) {
      setError(fallo.message);
    }
  }

  return (
    <section className="admin-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">AGENDA MÉDICA</p>
          <h1>Horarios de atención</h1>
          <p className="heading-copy">Define los rangos de atención y consulta los espacios que siguen disponibles.</p>
        </div>
      </div>

      <form className="appointment-filter-card schedule-form" onSubmit={guardar}>
        <div className="appointment-filter-heading"><div><h2>{editarId ? 'Modificar horario' : 'Registrar horario'}</h2><p>Los cruces con otros horarios activos del médico se rechazan.</p></div></div>
        <div className="schedule-fields">
          <label>Médico<select name="medico_id" required value={formulario.medico_id} onChange={actualizar}><option value="">Selecciona un médico</option>{medicos.map((medico) => <option key={medico.id} value={medico.id}>{medico.nombre}{medico.especialidad ? ` · ${medico.especialidad}` : ''}</option>)}</select></label>
          <label>Fecha<input name="fecha" type="date" required min={fechaLocal()} value={formulario.fecha} onChange={actualizar} /></label>
          <label>Desde<input name="hora_inicio" type="time" required value={formulario.hora_inicio} onChange={actualizar} /></label>
          <label>Hasta<input name="hora_fin" type="time" required value={formulario.hora_fin} onChange={actualizar} /></label>
          <label>Duración de cada cita<select name="intervalo_minutos" value={formulario.intervalo_minutos} onChange={actualizar}>{[15, 20, 30, 45, 60].map((minutos) => <option key={minutos} value={minutos}>{minutos} minutos</option>)}</select></label>
        </div>
        <div className="appointment-filter-actions">
          {editarId && <button className="secondary-button" type="button" onClick={cancelarEdicion}>Cancelar edición</button>}
          <button className="primary-button" type="submit" disabled={guardando || medicos.length === 0}>{guardando ? 'Guardando...' : editarId ? 'Guardar cambios' : 'Registrar horario'}</button>
        </div>
      </form>

      {error && <p className="form-error" role="alert">{error}</p>}
      {mensaje && <p className="form-success" role="status">{mensaje}</p>}
      {medicos.length === 0 && !cargando && <p className="empty-row">No hay médicos registrados para asignarles horarios.</p>}

      <section className="table-card schedule-table-card">
        <div className="table-heading"><div><h2>Horarios registrados</h2><p>{horarios.length} {horarios.length === 1 ? 'horario' : 'horarios'}</p></div></div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>MÉDICO</th><th>FECHA</th><th>ATENCIÓN</th><th>ESPACIOS</th><th>ESTADO</th><th>ACCIONES</th></tr></thead>
            <tbody>
              {horarios.map((horario) => (
                <tr key={horario.id}>
                  <td><strong>{horario.medico}</strong><small className="schedule-specialty">{horario.especialidad || 'Sin especialidad'}</small></td>
                  <td>{horario.fecha.split('-').reverse().join('/')}</td>
                  <td>{horario.hora_inicio}–{horario.hora_fin}<small className="schedule-specialty">Citas de {horario.intervalo_minutos} min</small></td>
                  <td><span className="schedule-free-count">{horario.total_disponibles} libres</span><small className="schedule-specialty">{horario.total_ocupados} ocupados</small></td>
                  <td><span className={`appointment-status ${horario.activo ? 'appointment-status-confirmada' : 'appointment-status-cancelada'}`}>{horario.activo ? 'Activo' : 'Inactivo'}</span></td>
                  <td><div className="schedule-actions"><button className="secondary-button" type="button" onClick={() => iniciarEdicion(horario)}>Editar</button><button className="text-button" type="button" onClick={() => cambiarActivo(horario)}>{horario.activo ? 'Desactivar' : 'Activar'}</button></div></td>
                </tr>
              ))}
              {!horarios.length && <tr><td colSpan="6" className="empty-row">{cargando ? 'Cargando horarios…' : 'Aún no se han registrado horarios.'}</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}
