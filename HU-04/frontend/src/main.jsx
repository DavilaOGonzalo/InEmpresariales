import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";

import { CrearUsuarioAdmin } from "./admin/CrearUsuarioAdmin";
import { EditarUsuarioAdmin } from "./admin/EditarUsuarioAdmin";
import { EstadoUsuarioAdmin } from "./admin/EstadoUsuarioAdmin";
import "./styles.css";

function AdminApp() {
  const [vista, setVista] = useState("crear");

  return (
    <>
      <nav className="admin-navigation" aria-label="Gestión de usuarios">
        <button
          type="button"
          className={vista === "crear" ? "active" : ""}
          onClick={() => setVista("crear")}
        >
          Registrar usuario
        </button>
        <button
          type="button"
          className={vista === "editar" ? "active" : ""}
          onClick={() => setVista("editar")}
        >
          Consultar y editar
        </button>
        <button
          type="button"
          className={vista === "estado" ? "active" : ""}
          onClick={() => setVista("estado")}
        >
          Estado de cuenta
        </button>
      </nav>
      {vista === "crear" ? (
        <CrearUsuarioAdmin />
      ) : vista === "editar" ? (
        <EditarUsuarioAdmin />
      ) : (
        <EstadoUsuarioAdmin />
      )}
    </>
  );
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AdminApp />
  </StrictMode>,
);
