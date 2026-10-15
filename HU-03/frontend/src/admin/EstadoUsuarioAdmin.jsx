import { useEffect, useState } from "react";

import {
  cambiarEstadoUsuarioAdmin,
  listarUsuariosAdmin,
  obtenerEstadoUsuarioAdmin,
} from "./usuarioAdminApi";

export function EstadoUsuarioAdmin() {
  const [usuarios, setUsuarios] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [estadoCuenta, setEstadoCuenta] = useState(null);
  const [status, setStatus] = useState({ type: "", message: "" });
  const [loading, setLoading] = useState(true);
  const [loadingState, setLoadingState] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let activo = true;
    listarUsuariosAdmin()
      .then((response) => {
        if (activo) setUsuarios(response.users || []);
      })
      .catch((error) => {
        if (activo) setStatus({ type: "error", message: error.message });
      })
      .finally(() => {
        if (activo) setLoading(false);
      });
    return () => {
      activo = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setEstadoCuenta(null);
      setLoadingState(false);
      return undefined;
    }

    let activo = true;
    setEstadoCuenta(null);
    setLoadingState(true);
    setStatus({ type: "", message: "" });
    obtenerEstadoUsuarioAdmin(selectedId)
      .then((response) => {
        if (activo) setEstadoCuenta(response.user);
      })
      .catch((error) => {
        if (activo) setStatus({ type: "error", message: error.message });
      })
      .finally(() => {
        if (activo) setLoadingState(false);
      });
    return () => {
      activo = false;
    };
  }, [selectedId]);

  const cambiarEstado = async () => {
    if (!estadoCuenta) return;
    setSaving(true);
    setStatus({ type: "", message: "" });
    try {
      const response = await cambiarEstadoUsuarioAdmin(
        estadoCuenta.id,
        !estadoCuenta.is_active,
      );
      setEstadoCuenta(response.user);
      setStatus({ type: "success", message: response.message });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="admin-page">
      <section className="admin-card" aria-labelledby="titulo-estado">
        <p className="eyebrow">EssAid · Gestión</p>
        <h1 id="titulo-estado">Estado de cuenta</h1>
        <p className="intro">
          Consulta el estado de una cuenta de usuario.
        </p>

        {status.message && (
          <div className={`status status-${status.type}`} role="status">
            {status.message}
          </div>
        )}

        <div className="user-selector">
          <label htmlFor="usuario-estado">Usuario</label>
          <select
            id="usuario-estado"
            value={selectedId}
            onChange={(event) => setSelectedId(event.target.value)}
            disabled={loading || loadingState || saving}
          >
            <option value="">
              {loading ? "Cargando usuarios…" : "Selecciona un usuario"}
            </option>
            {usuarios.map((usuario) => (
              <option key={usuario.id} value={usuario.id}>
                {usuario.email} · {usuario.rol}
              </option>
            ))}
          </select>
        </div>

        {loadingState && <p role="status">Consultando estado…</p>}
        {estadoCuenta && (
          <div className="account-state" aria-live="polite">
            <p>
              Estado actual:{" "}
              <strong>
                {estadoCuenta.is_active ? "Activa" : "Inactiva"}
              </strong>
            </p>
            <button type="button" onClick={cambiarEstado} disabled={saving}>
              {saving
                ? "Guardando…"
                : estadoCuenta.is_active
                  ? "Desactivar cuenta"
                  : "Activar cuenta"}
            </button>
          </div>
        )}
      </section>
    </main>
  );
}
