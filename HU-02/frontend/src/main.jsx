import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";

import { CrearUsuarioAdmin } from "./admin/CrearUsuarioAdmin";
import { EditarUsuarioAdmin } from "./admin/EditarUsuarioAdmin";
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
      </nav>
      {vista === "crear" ? <CrearUsuarioAdmin /> : <EditarUsuarioAdmin />}
    </>
  );
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AdminApp />
  </StrictMode>,
);
