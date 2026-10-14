import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { CrearUsuarioAdmin } from "./admin/CrearUsuarioAdmin";
import "./styles.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <CrearUsuarioAdmin />
  </StrictMode>,
);
