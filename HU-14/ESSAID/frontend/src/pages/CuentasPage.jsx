import CuentaForm from '../components/CuentaForm.jsx';
import Cuentas from '../components/Cuentas.jsx';
import DetalleCuenta from '../components/DetalleCuenta.jsx';

export default function CuentasPage({
  pagina, urlRuta, rutaLista, cuentas, totalCuentas, navegar,
  guardarCuenta, errorFormulario, procesando, eliminarCuenta,
  cambiarEstadoCuenta, mensajeExito,
}) {
  if (pagina === '/admin/cuentas/nueva') {
    return <CuentaForm onSave={guardarCuenta} onCancel={() => navegar(rutaLista)} error={errorFormulario} procesando={procesando} />;
  }

  const editar = pagina.match(/^\/admin\/cuentas\/(\d+)\/editar$/);
  const ver = pagina.match(/^\/admin\/cuentas\/(\d+)$/);
  if (editar || ver) {
    const cuentaId = Number((editar || ver)[1]);
    const cuenta = cuentas.find((item) => item.id === cuentaId);
    if (!cuenta) {
      return <section className="admin-content"><p className="form-error">No se encontro esa cuenta.</p><button className="secondary-button" onClick={() => navegar(rutaLista)}>Volver a las cuentas</button></section>;
    }
    return editar
      ? <CuentaForm cuenta={cuenta} onSave={guardarCuenta} onCancel={() => navegar(rutaLista)} error={errorFormulario} procesando={procesando} />
      : <DetalleCuenta cuenta={cuenta} rutaLista={rutaLista} urlRuta={urlRuta} navegar={navegar} />;
  }

  if (pagina === '/admin/cuentas') {
    return <Cuentas cuentas={cuentas} totalCuentas={totalCuentas} navegar={navegar} onDelete={eliminarCuenta} onToggleStatus={cambiarEstadoCuenta} procesando={procesando} mensajeExito={mensajeExito} consultaInicial={urlRuta.search} />;
  }
  return null;
}
