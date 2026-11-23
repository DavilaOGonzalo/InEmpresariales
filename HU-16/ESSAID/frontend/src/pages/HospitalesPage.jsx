import Hospitales from '../components/Hospitales.jsx';
import HospitalForm from '../components/HospitalForm.jsx';
import HospitalDetalle from '../components/HospitalDetalle.jsx';

export default function HospitalesPage({
  pagina, hospitales, navegar, mensajeHospital, cambiarEstadoHospital,
  procesando, errorCargaDatos, errorHospital, guardarHospital,
}) {
  if (pagina === '/admin/hospitales/nuevo') {
    return <HospitalForm onSave={guardarHospital} onCancel={() => navegar('/admin/hospitales')} error={errorHospital} procesando={procesando} />;
  }

  const editar = pagina.match(/^\/admin\/hospitales\/(\d+)\/editar$/);
  const detalle = pagina.match(/^\/admin\/hospitales\/(\d+)$/);
  if (editar || detalle) {
    const hospitalId = Number((editar || detalle)[1]);
    const hospital = hospitales.find((item) => item.id === hospitalId);
    if (!hospital) {
      return <section className="admin-content"><p className="form-error">No se encontro ese hospital.</p><button className="secondary-button" onClick={() => navegar('/admin/hospitales')}>Volver a hospitales</button></section>;
    }
    return editar
      ? <HospitalForm key={hospital.id} hospital={hospital} onSave={guardarHospital} onCancel={() => navegar('/admin/hospitales')} error={errorHospital} procesando={procesando} />
      : <HospitalDetalle hospital={hospital} navegar={navegar} mensaje={mensajeHospital} />;
  }

  if (pagina === '/admin/hospitales') {
    return <Hospitales hospitales={hospitales} navegar={navegar} mensaje={mensajeHospital} onToggleStatus={cambiarEstadoHospital} procesando={procesando} errorCarga={errorCargaDatos} />;
  }
  return null;
}
