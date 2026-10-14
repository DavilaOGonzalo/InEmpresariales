import { useEffect, useState } from "react";

import {
  actualizarUsuarioAdmin,
  listarUsuariosAdmin,
  obtenerUsuarioAdmin,
} from "./usuarioAdminApi";
import { ROLES } from "./CrearUsuarioAdmin";

const EMPTY_FORM = {
  first_name: "",
  last_name: "",
  email: "",
  rol: "",
  tipo_documento: "",
  numero_documento: "",
  caracter_verificador: "",
  fecha_nacimiento: "",
  celular: "",
};

const PATIENT_FIELDS = [
  "tipo_documento",
  "numero_documento",
  "caracter_verificador",
  "fecha_nacimiento",
  "celular",
];

function FieldError({ errors, name }) {
  const messages = errors[name] || [];
  return messages.length ? (
    <p className="field-error" role="alert">
      {messages.join(" ")}
    </p>
  ) : null;
}

export function EditarUsuarioAdmin({ puedeCrearAdministrador = false }) {
  const [usuarios, setUsuarios] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState({ type: "", message: "" });
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [loadingUser, setLoadingUser] = useState(false);
  const [saving, setSaving] = useState(false);

  const esPaciente = form.rol === "PACIENTE";
  const esDni = esPaciente && form.tipo_documento === "DNI";
  const roles = puedeCrearAdministrador
    ? ROLES
    : ROLES.filter(
        (role) => role.value !== "ADMINISTRADOR" || role.value === form.rol,
      );

  const cargarUsuarios = async ({ limpiarEstado = true } = {}) => {
    setLoadingUsers(true);
    try {
      const response = await listarUsuariosAdmin();
      setUsuarios(response.users || []);
      if (limpiarEstado) setStatus({ type: "", message: "" });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoadingUsers(false);
    }
  };

  useEffect(() => {
    cargarUsuarios();
  }, []);

  const consultarUsuario = async (id = selectedId) => {
    if (!id) return;
    setSelectedId(String(id));
    setLoadingUser(true);
    setErrors({});
    setStatus({ type: "", message: "" });
    try {
      const response = await obtenerUsuarioAdmin(id);
      setForm({ ...EMPTY_FORM, ...response.user });
    } catch (error) {
      setForm(EMPTY_FORM);
      setStatus({ type: "error", message: error.message });
      setErrors(error.errors || {});
    } finally {
      setLoadingUser(false);
    }
  };

  const update = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: value,
      ...(name === "tipo_documento" && value !== "DNI"
        ? { caracter_verificador: "" }
        : {}),
    }));
    setErrors((current) => ({ ...current, [name]: undefined }));
    setStatus({ type: "", message: "" });
  };

  const submit = async (event) => {
    event.preventDefault();
    if (!selectedId) return;

    setSaving(true);
    setErrors({});
    setStatus({ type: "", message: "" });
    const payload = {
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      rol: form.rol,
    };
    if (esPaciente) {
      PATIENT_FIELDS.forEach((field) => {
        payload[field] = form[field];
      });
    }

    try {
      const response = await actualizarUsuarioAdmin(selectedId, payload);
      setForm({ ...EMPTY_FORM, ...response.user });
      await cargarUsuarios({ limpiarEstado: false });
      setStatus({ type: "success", message: response.message });
    } catch (error) {
      setErrors(error.errors || {});
      setStatus({ type: "error", message: error.message });
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="admin-page">
      <section className="admin-card" aria-labelledby="titulo-edicion">
        <p className="eyebrow">EssAid · Gestión</p>
        <h1 id="titulo-edicion">Consultar y editar usuario</h1>
        <p className="intro">
          Selecciona una cuenta para consultar y actualizar solo sus datos autorizados.
        </p>

        {status.message && (
          <div className={`status status-${status.type}`} role="status">
            {status.message}
          </div>
        )}
        <FieldError errors={errors} name="__all__" />

        <div className="user-selector">
          <label htmlFor="usuario-seleccionado">Usuario</label>
          <select
            id="usuario-seleccionado"
            value={selectedId}
            onChange={(event) => {
              setSelectedId(event.target.value);
              setForm(EMPTY_FORM);
              setErrors({});
              setStatus({ type: "", message: "" });
            }}
            disabled={loadingUsers || loadingUser}
          >
            <option value="">
              {loadingUsers ? "Cargando usuarios…" : "Selecciona un usuario"}
            </option>
            {usuarios.map((usuario) => (
              <option key={usuario.id} value={usuario.id}>
                {usuario.email} · {usuario.rol}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="secondary-button"
            onClick={() => consultarUsuario()}
            disabled={!selectedId || loadingUser}
          >
            {loadingUser ? "Consultando…" : "Consultar"}
          </button>
        </div>

        {form.rol && (
          <form onSubmit={submit} noValidate>
            <div className="field-grid">
              <label>
                Nombres
                <input name="first_name" value={form.first_name} onChange={update} required />
                <FieldError errors={errors} name="first_name" />
              </label>
              <label>
                Apellidos
                <input name="last_name" value={form.last_name} onChange={update} required />
                <FieldError errors={errors} name="last_name" />
              </label>
            </div>

            <label>
              Correo electrónico
              <input name="email" type="email" value={form.email} onChange={update} required />
              <FieldError errors={errors} name="email" />
            </label>

            <label>
              Rol
              <select name="rol" value={form.rol} onChange={update} required>
                {roles.map((role) => (
                  <option key={role.value} value={role.value}>
                    {role.label}
                  </option>
                ))}
              </select>
              <FieldError errors={errors} name="rol" />
            </label>

            {esPaciente && (
              <fieldset>
                <legend>Datos del paciente</legend>
                <div className="field-grid">
                  <label>
                    Tipo de documento
                    <select name="tipo_documento" value={form.tipo_documento} onChange={update} required>
                      <option value="">Selecciona un tipo</option>
                      <option value="DNI">DNI</option>
                      <option value="CE">Carné de extranjería</option>
                    </select>
                    <FieldError errors={errors} name="tipo_documento" />
                  </label>
                  <label>
                    Número de documento
                    <input name="numero_documento" value={form.numero_documento} onChange={update} required />
                    <FieldError errors={errors} name="numero_documento" />
                  </label>
                </div>
                {esDni && (
                  <label>
                    Carácter verificador
                    <input name="caracter_verificador" maxLength="1" value={form.caracter_verificador} onChange={update} required />
                    <FieldError errors={errors} name="caracter_verificador" />
                  </label>
                )}
                <div className="field-grid">
                  <label>
                    Fecha de nacimiento
                    <input name="fecha_nacimiento" type="date" value={form.fecha_nacimiento} onChange={update} required />
                    <FieldError errors={errors} name="fecha_nacimiento" />
                  </label>
                  <label>
                    Celular
                    <input name="celular" type="tel" value={form.celular} onChange={update} required />
                    <FieldError errors={errors} name="celular" />
                  </label>
                </div>
              </fieldset>
            )}

            <button type="submit" disabled={saving || loadingUser}>
              {saving ? "Guardando…" : "Guardar cambios"}
            </button>
          </form>
        )}
      </section>
    </main>
  );
}
