import { useState } from "react";

import { crearUsuarioAdmin } from "./usuarioAdminApi";
import { ROLES } from "./roles";

const EMPTY_FORM = {
  first_name: "",
  last_name: "",
  email: "",
  password1: "",
  password2: "",
  rol: "PACIENTE",
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

export function CrearUsuarioAdmin({ puedeCrearAdministrador = false, onSuccess }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState({ type: "", message: "" });
  const [saving, setSaving] = useState(false);

  const esPaciente = form.rol === "PACIENTE";
  const esDni = esPaciente && form.tipo_documento === "DNI";
  const roles = puedeCrearAdministrador
    ? ROLES
    : ROLES.filter((role) => role.value !== "ADMINISTRADOR");

  const update = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: undefined }));
    setStatus({ type: "", message: "" });
  };

  const submit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setErrors({});
    setStatus({ type: "", message: "" });

    const payload = { ...form };
    if (!esPaciente) {
      PATIENT_FIELDS.forEach((field) => delete payload[field]);
    } else if (!esDni) {
      delete payload.caracter_verificador;
    }

    try {
      const response = await crearUsuarioAdmin(payload);
      setForm(EMPTY_FORM);
      setStatus({ type: "success", message: response.message });
      onSuccess?.(response.user);
    } catch (error) {
      setErrors(error.errors || {});
      setStatus({ type: "error", message: error.message });
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="admin-page">
      <section className="admin-card" aria-labelledby="titulo-registro">
        <p className="eyebrow">EssAid · Gestión</p>
        <h1 id="titulo-registro">Crear cuenta de usuario</h1>
        <p className="intro">Registra los datos y asigna un rol.</p>

        {status.message && (
          <div className={`status status-${status.type}`} role="status">
            {status.message}
          </div>
        )}
        <FieldError errors={errors} name="__all__" />

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
          <div className="field-grid">
            <label>
              Contraseña
              <input name="password1" type="password" value={form.password1} onChange={update} required />
              <FieldError errors={errors} name="password1" />
            </label>
            <label>
              Confirmar contraseña
              <input name="password2" type="password" value={form.password2} onChange={update} required />
              <FieldError errors={errors} name="password2" />
            </label>
          </div>

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

          <button type="submit" disabled={saving}>
            {saving ? "Registrando…" : "Registrar usuario"}
          </button>
        </form>
      </section>
    </main>
  );
}
