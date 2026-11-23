import React from 'react';
import ServiciosMedicos from '../components/ServiciosMedicos.jsx';
import ServicioMedicoForm from '../components/ServicioMedicoForm.jsx';
import AsignarServicioForm from '../components/AsignarServicioForm.jsx';
import ServiciosAsignados from '../components/ServiciosAsignados.jsx';
import ServicioDetalle from '../components/ServicioDetalle.jsx';

export default function ServiciosPage({
  pagina, urlRuta, servicios, asignaciones, hospitales, navegar,
  mensajeServicio, cambiarEstadoServicio, procesando, errorCargaDatos,
  errorServicio, guardarServicio, errorAsignacion, guardarAsignacion,
  mensajeAsignacion,
}) {
  if (pagina === '/admin/servicios/nuevo') {
    return <ServicioMedicoForm onSave={guardarServicio} onCancel={() => navegar('/admin/servicios')} error={errorServicio} procesando={procesando} />;
  }

  const editar = pagina.match(/^\/admin\/servicios\/(\d+)\/editar$/);
  const detalle = pagina.match(/^\/admin\/servicios\/(\d+)$/);
  if (editar || detalle) {
    const servicioId = Number((editar || detalle)[1]);
    const servicio = servicios.find((item) => item.id === servicioId);
    if (!servicio) {
      return <section className="admin-content"><p className="form-error">No se encontro ese servicio.</p><button className="secondary-button" onClick={() => navegar('/admin/servicios')}>Volver al catalogo</button></section>;
    }
    return editar
      ? <ServicioMedicoForm key={servicio.id} servicio={servicio} onSave={guardarServicio} onCancel={() => navegar('/admin/servicios')} error={errorServicio} procesando={procesando} />
      : <ServicioDetalle servicio={servicio} asignaciones={asignaciones} navegar={navegar} />;
  }

  if (pagina === '/admin/servicios/asignar') {
    return <AsignarServicioForm key={urlRuta.search} servicios={servicios} hospitales={hospitales} servicioInicial={urlRuta.searchParams.get('servicio')} onSave={guardarAsignacion} onCancel={() => navegar('/admin/servicios')} error={errorAsignacion} procesando={procesando} />;
  }
  if (pagina === '/admin/servicios/asignados') {
    return <ServiciosAsignados asignaciones={asignaciones} navegar={navegar} mensaje={mensajeAsignacion} />;
  }
  if (pagina === '/admin/servicios') {
    return <ServiciosMedicos servicios={servicios} asignaciones={asignaciones} navegar={navegar} mensaje={mensajeServicio} onToggleStatus={cambiarEstadoServicio} procesando={procesando} errorCarga={errorCargaDatos} />;
  }
  return null;
}
