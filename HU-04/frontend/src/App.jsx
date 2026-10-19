import { useMemo, useState } from "react";

import { CrearUsuarioAdmin } from "./admin/CrearUsuarioAdmin";
import { EditarUsuarioAdmin } from "./admin/EditarUsuarioAdmin";
import { EstadoUsuarioAdmin } from "./admin/EstadoUsuarioAdmin";
import "./App.css";
import "./index.css";
import "./styles.css";

const usuariosIniciales = [
  {
    id: 101,
    first_name: "Ana",
    last_name: "Torres",
    email: "ana.torres@essaid.test",
    rol: "PACIENTE",
    is_active: true,
  },
  {
    id: 102,
    first_name: "Luis",
    last_name: "Mendoza",
    email: "luis.mendoza@essaid.test",
    rol: "PROFESIONAL_SALUD",
    is_active: true,
  },
  {
    id: 103,
    first_name: "Camila",
    last_name: "Rojas",
    email: "camila.rojas@essaid.test",
    rol: "PACIENTE",
    is_active: false,
  },
  {
    id: 104,
    first_name: "Jorge",
    last_name: "Salazar",
    email: "jorge.salazar@essaid.test",
    rol: "PROFESIONAL_SALUD",
    is_active: true,
  },
  {
    id: 105,
    first_name: "Valeria",
    last_name: "Huamán",
    email: "valeria.huaman@essaid.test",
    rol: "PACIENTE",
    is_active: true,
  },
];

const pacientesInvestigacion = [
  {
    id: 201,
    usuario: {
      id: 101,
      email: "ana.torres@essaid.test",
      first_name: "Ana",
      last_name: "Torres",
      rol: "PACIENTE",
      is_active: true,
    },
    tipo_documento: "DNI",
    numero_documento: "74231568",
    caracter_verificador: "4",
    fecha_nacimiento: "1994-05-12",
    celular: "987654321",
    consultas: [
      {
        id: 1,
        fecha: "2026-10-20",
        especialidad: "Medicina general",
        estado: "Confirmada",
        importe: "45.00",
      },
      {
        id: 2,
        fecha: "2026-11-04",
        especialidad: "Nutrición",
        estado: "Pendiente",
        importe: "35.50",
      },
    ],
  },
  {
    id: 202,
    usuario: {
      id: 102,
      email: "luis.mendoza@essaid.test",
      first_name: "Luis",
      last_name: "Mendoza",
      rol: "PROFESIONAL_SALUD",
      is_active: true,
    },
    tipo_documento: "DNI",
    numero_documento: "71384629",
    caracter_verificador: "8",
    fecha_nacimiento: "1988-09-21",
    celular: "986123450",
    consultas: [
      {
        id: 3,
        fecha: "2026-10-22",
        especialidad: "Cardiología",
        estado: "Confirmada",
        importe: "80.00",
      },
    ],
  },
  {
    id: 203,
    usuario: {
      id: 103,
      email: "camila.rojas@essaid.test",
      first_name: "Camila",
      last_name: "Rojas",
      rol: "PACIENTE",
      is_active: false,
    },
    tipo_documento: "CE",
    numero_documento: "CE0098123",
    caracter_verificador: "",
    fecha_nacimiento: "1997-01-30",
    celular: "985442178",
    consultas: [
      {
        id: 4,
        fecha: "2026-10-25",
        especialidad: "Psicología",
        estado: "Cancelada",
        importe: "55.00",
      },
      {
        id: 5,
        fecha: "2026-11-10",
        especialidad: "Medicina general",
        estado: "Pendiente",
        importe: "45.00",
      },
    ],
  },
  {
    id: 204,
    usuario: {
      id: 104,
      email: "jorge.salazar@essaid.test",
      first_name: "Jorge",
      last_name: "Salazar",
      rol: "PROFESIONAL_SALUD",
      is_active: true,
    },
    tipo_documento: "DNI",
    numero_documento: "70451236",
    caracter_verificador: "1",
    fecha_nacimiento: "1985-07-08",
    celular: "984771230",
    consultas: [
      {
        id: 6,
        fecha: "2026-10-28",
        especialidad: "Dermatología",
        estado: "Confirmada",
        importe: "65.00",
      },
    ],
  },
  {
    id: 205,
    usuario: {
      id: 105,
      email: "valeria.huaman@essaid.test",
      first_name: "Valeria",
      last_name: "Huamán",
      rol: "PACIENTE",
      is_active: true,
    },
    tipo_documento: "DNI",
    numero_documento: "75628941",
    caracter_verificador: "6",
    fecha_nacimiento: "1992-12-17",
    celular: "983225614",
    consultas: [
      {
        id: 7,
        fecha: "2026-11-02",
        especialidad: "Odontología",
        estado: "Confirmada",
        importe: "70.00",
      },
      {
        id: 8,
        fecha: "2026-11-16",
        especialidad: "Nutrición",
        estado: "Pendiente",
        importe: "35.50",
      },
    ],
  },
];

function LaboratorioReact() {
  const [usuarios, setUsuarios] = useState(usuariosIniciales);
  const [mostrarListaVacia, setMostrarListaVacia] = useState(
    () => new URLSearchParams(window.location.search).get("empty") === "1",
  );

  const usuariosVisibles = mostrarListaVacia ? [] : usuarios;
  const usuariosActivos = useMemo(
    () => usuarios.filter((usuario) => usuario.is_active).length,
    [usuarios],
  );
  const totalConsultas = pacientesInvestigacion.reduce(
    (total, paciente) => total + paciente.consultas.length,
    0,
  );

  const alternarEstadoAna = () => {
    setUsuarios((actuales) =>
      actuales.map((usuario) =>
        usuario.id === 101
          ? { ...usuario, is_active: !usuario.is_active }
          : usuario,
      ),
    );
  };

  return (
    <main className="lab-page" aria-labelledby="titulo-laboratorio">
      <section className="lab-hero">
        <div>
          <p className="lab-kicker">Semana 9 · React + Vite</p>
          <h1 id="titulo-laboratorio">Panel de datos EssAid</h1>
          <p className="lab-lead">
            {"Una interfaz SPA para explorar usuarios y pacientes con "}
            <strong>{usuariosActivos} cuentas activas</strong>
            {" y "}
            <strong>{totalConsultas} consultas anidadas</strong>.
          </p>
        </div>
        <div className="lab-code-card" aria-label="Expresión calculada">
          <span>ID formateado</span>
          <strong>{Number(usuariosVisibles[0]?.id ?? 0).toFixed(2)}</strong>
          <small>Number(id).toFixed(2)</small>
        </div>
      </section>

      <section className="lab-controls" aria-label="Demostraciones interactivas">
        <button type="button" onClick={alternarEstadoAna}>
          Cambiar estado de Ana Torres
        </button>
        <button
          type="button"
          className="lab-secondary-button"
          onClick={() => setMostrarListaVacia((actual) => !actual)}
        >
          {mostrarListaVacia ? "Restaurar registros" : "Probar lista vacía"}
        </button>
        <span className="lab-hint">
          Los datos son manuales para demostrar el flujo de React.
        </span>
      </section>

      <div className="lab-grid">
        <section className="lab-panel" aria-labelledby="usuarios-titulo">
          <div className="panel-heading">
            <div>
              <p className="lab-kicker">Entidad principal</p>
              <h2 id="usuarios-titulo">Usuarios</h2>
            </div>
            <span className="count-badge">{usuariosVisibles.length}</span>
          </div>
          <p className="panel-description">
            Lista construida con <code>map()</code>, <code>key={"{id}"}</code> y
            un estado condicional.
          </p>
          {usuariosVisibles.length === 0 ? (
            <p className="empty-state" role="status">
              No hay registros
            </p>
          ) : (
            <ul className="entity-list">
              {usuariosVisibles.map((usuario) => (
                <li className="entity-card" key={usuario.id}>
                  <div className="entity-card-heading">
                    <div>
                      <h3>
                        {usuario.first_name} {usuario.last_name}
                      </h3>
                      <p>{usuario.email}</p>
                    </div>
                    <span
                      className={`status-pill ${
                        usuario.is_active ? "status-pill-active" : "status-pill-inactive"
                      }`}
                    >
                      {usuario.is_active ? "Activa" : "Inactiva"}
                    </span>
                  </div>
                  <dl className="entity-details">
                    <div>
                      <dt>Rol</dt>
                      <dd>{usuario.rol.replace("_", " ")}</dd>
                    </div>
                    <div>
                      <dt>ID decimal</dt>
                      <dd>{Number(usuario.id).toFixed(2)}</dd>
                    </div>
                  </dl>
                  <p className="conditional-copy">
                    {usuario.is_active
                      ? "La cuenta puede iniciar sesión."
                      : "La cuenta tiene el acceso restringido."}
                    {usuario.is_active && <span> · Seguimiento disponible.</span>}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="lab-panel" aria-labelledby="pacientes-titulo">
          <div className="panel-heading">
            <div>
              <p className="lab-kicker">Relación 1:1 + 1:N</p>
              <h2 id="pacientes-titulo">Pacientes y consultas</h2>
            </div>
            <span className="count-badge">{pacientesInvestigacion.length}</span>
          </div>
          <p className="panel-description">
            Cada paciente contiene su usuario relacionado y una lista de
            consultas representada con un <code>map()</code> anidado.
          </p>
          <ul className="patient-list">
            {pacientesInvestigacion.map((paciente) => {
              const totalPaciente = paciente.consultas.reduce(
                (total, consulta) => total + Number(consulta.importe),
                0,
              );

              return (
                <li className="patient-card" key={paciente.id}>
                  <div className="entity-card-heading">
                    <div>
                      <h3>
                        {paciente.usuario.first_name} {paciente.usuario.last_name}
                      </h3>
                      <p>
                        {paciente.tipo_documento}: {paciente.numero_documento}
                      </p>
                    </div>
                    <span className="patient-id">#{paciente.id}</span>
                  </div>
                  <ul className="nested-list">
                    {paciente.consultas.map((consulta) => (
                      <li key={consulta.id}>
                        <div>
                          <strong>{consulta.especialidad}</strong>
                          <span>{consulta.fecha}</span>
                        </div>
                        <span className="consultation-state">{consulta.estado}</span>
                      </li>
                    ))}
                  </ul>
                  <p
                    className="patient-total"
                    style={{
                      color: paciente.usuario.is_active ? "#176b4d" : "#9b3d36",
                    }}
                  >
                    Total de consultas: S/ {totalPaciente.toFixed(2)}
                  </p>
                </li>
              );
            })}
          </ul>
        </section>
      </div>

      <aside className="lab-note">
        <strong>Justificación del flujo:</strong> JSX reemplaza las etiquetas y
        bucles de un Template de Django con expresiones entre llaves,
        <code>map()</code> y condicionales de JavaScript. La siguiente etapa
        será reemplazar los arreglos manuales por consultas a la API REST.
      </aside>
    </main>
  );
}

function App() {
  const [vista, setVista] = useState("laboratorio");

  const opciones = [
    { id: "laboratorio", label: "Laboratorio React" },
    { id: "crear", label: "Registrar usuario" },
    { id: "editar", label: "Consultar y editar" },
    { id: "estado", label: "Estado de cuenta" },
  ];

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-block">
          <p className="brand-mark">EssAid</p>
          <p className="brand-subtitle">Salud conectada</p>
        </div>
        <nav className="app-navigation" aria-label="Secciones de la aplicación">
          {opciones.map((opcion) => (
            <button
              type="button"
              key={opcion.id}
              className={vista === opcion.id ? "active" : ""}
              onClick={() => setVista(opcion.id)}
            >
              {opcion.label}
            </button>
          ))}
        </nav>
      </header>

      {vista === "laboratorio" ? (
        <LaboratorioReact />
      ) : vista === "crear" ? (
        <CrearUsuarioAdmin />
      ) : vista === "editar" ? (
        <EditarUsuarioAdmin />
      ) : (
        <EstadoUsuarioAdmin />
      )}
    </div>
  );
}

export default App;
