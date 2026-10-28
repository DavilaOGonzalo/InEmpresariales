import React, { useEffect, useState } from 'react';

const VACIO = {
  nombre: '', apellido: '', dni: '', correo: '', telefono: '', rol: '', contrasena: '', permisos: [],
  fecha_nacimiento: '', identificacion_complementaria: '', sexo: '', especialidad: '',
  cmp: '', direccion: '', informacion_contacto: '', tipo_sangre: '',
  contacto_emergencia: '', telefono_emergencia: '',
};

const PERMISOS_POR_ROL = {
  medico: [
    { clave: 'paciente.leer', texto: 'Leer información de pacientes' },
    { clave: 'paciente.editar', texto: 'Editar información de pacientes' },
    { clave: 'medico.leer_propio', texto: 'Leer su propia información' },
    { clave: 'medico.editar_propio', texto: 'Editar su propia información' },
  ],
  paciente: [
    { clave: 'paciente.leer_propio', texto: 'Leer su propia información' },
    { clave: 'paciente.editar_propio', texto: 'Editar su propia información' },
    { clave: 'medico.leer', texto: 'Leer información del médico' },
  ],
};

const PERMISOS_INICIALES = {
  medico: ['paciente.leer', 'paciente.editar', 'medico.leer_propio', 'medico.editar_propio'],
  paciente: ['paciente.leer_propio', 'paciente.editar_propio', 'medico.leer'],
};

function calcularEdad(fecha) {
  if (!fecha) return null;
  const [anio, mes, dia] = fecha.split('-').map(Number);
  const hoy = new Date();
  return hoy.getFullYear() - anio - ((hoy.getMonth() + 1 < mes || (hoy.getMonth() + 1 === mes && hoy.getDate() < dia)) ? 1 : 0);
}

export default function CuentaForm({ cuenta, onSave, onCancel, error, procesando }) {
  const [datos, setDatos] = useState(VACIO);
  const [erroresCampos, setErroresCampos] = useState({});
  const esEdicion = Boolean(cuenta);
  const esMedico = datos.rol === 'medico';
  const esPaciente = datos.rol === 'paciente';

  useEffect(() => {
    setDatos(cuenta ? { ...VACIO, ...cuenta, contrasena: '' } : VACIO);
  }, [cuenta]);

  function actualizar(evento) {
    const { name, value } = evento.target;
    setErroresCampos((actuales) => ({ ...actuales, [name]: '' }));
    setDatos((actuales) => name === 'rol'
      ? { ...actuales, rol: value, permisos: PERMISOS_INICIALES[value] || [] }
      : { ...actuales, [name]: value });
  }

  function cambiarPermiso(clave) {
    setDatos((actuales) => ({
      ...actuales,
      permisos: actuales.permisos.includes(clave)
        ? actuales.permisos.filter((permiso) => permiso !== clave)
        : [...actuales.permisos, clave],
    }));
  }

  function enviar(evento) {
    evento.preventDefault();
    const errores = {};
    if (esMedico) {
      if (!datos.fecha_nacimiento) errores.fecha_nacimiento = 'Ingresa la fecha de nacimiento.';
      else if (datos.fecha_nacimiento > new Date().toISOString().slice(0, 10)) errores.fecha_nacimiento = 'La fecha no puede ser futura.';
      if (!datos.sexo) errores.sexo = 'Selecciona el sexo del médico.';
      if (!datos.especialidad?.trim()) errores.especialidad = 'Ingresa la especialidad médica.';
      if (!datos.cmp?.trim()) errores.cmp = 'Ingresa el número CMP.';
      else if (datos.cmp.trim().length > 20) errores.cmp = 'El CMP admite hasta 20 caracteres.';
    }
    setErroresCampos(errores);
    if (Object.keys(errores).length) return;
    onSave(datos);
  }

  function campoValidado(nombre, props = {}) {
    return { ...props, 'aria-invalid': Boolean(erroresCampos[nombre]) };
  }

  return (
    <section className="admin-content account-form-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">GESTION DE ACCESOS</p>
          <h1>{esEdicion ? 'Editar cuenta' : 'Crear cuenta'}</h1>
          <p className="heading-copy">{esEdicion ? 'Actualiza los datos del usuario.' : 'Crea el acceso y el perfil del usuario.'}</p>
        </div>
      </div>

      <form className="account-form-card" onSubmit={enviar}>
        <div className="account-form-grid">
          <label>Nombre<input name="nombre" value={datos.nombre} onChange={actualizar} autoComplete="given-name" required /></label>
          <label>Apellido<input name="apellido" value={datos.apellido} onChange={actualizar} autoComplete="family-name" required /></label>
          <label>DNI<input name="dni" inputMode="numeric" pattern="[0-9]{8}" minLength={8} maxLength={8} value={datos.dni || ''} onChange={actualizar} required /></label>
          <label>Correo<input name="correo" type="email" pattern="[^@\s]+@(tecsup\.edu\.pe|gmail\.com)" value={datos.correo || ''} onChange={actualizar} required /></label>
          <label>Telefono<input name="telefono" type="tel" inputMode="numeric" pattern="[0-9]{9}" minLength={9} maxLength={9} value={datos.telefono || ''} onChange={actualizar} required /></label>
          <label>Rol<select name="rol" value={datos.rol || ''} onChange={actualizar} required><option value="">Selecciona un rol</option><option value="paciente">Paciente</option><option value="medico">Medico</option></select></label>
          {!esEdicion && <label>Contrasena inicial<input name="contrasena" type="password" autoComplete="new-password" value={datos.contrasena} onChange={actualizar} required /></label>}
        </div>

        {esEdicion && <label className="account-password-field">{cuenta.tiene_cuenta ? 'Nueva contrasena (opcional)' : 'Contrasena inicial para crear el acceso (opcional)'}<input name="contrasena" type="password" autoComplete="new-password" value={datos.contrasena} onChange={actualizar} /><small>Deja el campo vacio para no cambiar la contrasena.</small></label>}

        {(esMedico || esPaciente) && <section className="role-fields permissions-fields">
          <h2>Permisos de acceso</h2>
          <p className="permissions-copy">Elige si esta cuenta puede leer o editar cada tipo de información.</p>
          <div className="permission-list">
            {PERMISOS_POR_ROL[datos.rol].map((permiso) => <label className="permission-option" key={permiso.clave}>
              <input type="checkbox" checked={datos.permisos.includes(permiso.clave)} onChange={() => cambiarPermiso(permiso.clave)} />
              <span>{permiso.texto}</span>
            </label>)}
          </div>
          {esPaciente && <small className="field-help">El paciente solo puede editar su propia información; los datos del médico son de solo lectura.</small>}
        </section>}

        {esMedico && <section className="role-fields">
          <h2>Datos de medico</h2>
          <div className="account-form-grid">
            <label>Fecha de nacimiento<input {...campoValidado('fecha_nacimiento')} name="fecha_nacimiento" type="date" value={datos.fecha_nacimiento || ''} onChange={actualizar} required />{erroresCampos.fecha_nacimiento && <small className="field-validation-error">{erroresCampos.fecha_nacimiento}</small>}</label>
            <label>Edad<input value={calcularEdad(datos.fecha_nacimiento) ?? ''} readOnly placeholder="Se calcula con la fecha de nacimiento" /></label>
            <label><span>Identificacion adicional <small className="field-optional">(opcional)</small></span><input name="identificacion_complementaria" maxLength={100} placeholder="Pasaporte u otro documento, si aplica" value={datos.identificacion_complementaria || ''} onChange={actualizar} /><small className="field-help">Dejala vacia si no se necesita otro documento aparte del DNI.</small></label>
            <label>Sexo<select {...campoValidado('sexo')} name="sexo" value={datos.sexo || ''} onChange={actualizar} required><option value="">Selecciona una opcion</option><option value="femenino">Femenino</option><option value="masculino">Masculino</option><option value="otro">Otro</option><option value="no_especificado">Prefiero no decir</option></select>{erroresCampos.sexo && <small className="field-validation-error">{erroresCampos.sexo}</small>}</label>
            <label>Especialidad medica<input {...campoValidado('especialidad')} name="especialidad" maxLength={100} placeholder="Ej.: Cardiologia, pediatria" value={datos.especialidad || ''} onChange={actualizar} required />{erroresCampos.especialidad && <small className="field-validation-error">{erroresCampos.especialidad}</small>}</label>
            <label>Numero CMP<input {...campoValidado('cmp')} name="cmp" maxLength={20} placeholder="Numero de colegiatura del medico" value={datos.cmp || ''} onChange={actualizar} required />{erroresCampos.cmp && <small className="field-validation-error">{erroresCampos.cmp}</small>}<small>Es el numero asignado por el Colegio Medico del Peru; no es el DNI. Verificalo antes de guardarlo.</small></label>
            <label><span>Direccion <small className="field-optional">(opcional)</small></span><textarea name="direccion" rows="3" value={datos.direccion || ''} onChange={actualizar} /></label>
          </div>
        </section>}

        {esPaciente && <section className="role-fields">
          <h2>Datos de paciente</h2>
          <div className="account-form-grid">
            <label>Fecha de nacimiento<input name="fecha_nacimiento" type="date" value={datos.fecha_nacimiento || ''} onChange={actualizar} required /></label>
            <label>Edad<input value={calcularEdad(datos.fecha_nacimiento) ?? ''} readOnly placeholder="Se calcula con la fecha de nacimiento" /></label>
            <label><span>Sexo <small className="field-optional">(opcional)</small></span><select name="sexo" value={datos.sexo || ''} onChange={actualizar}><option value="">Selecciona una opcion</option><option value="femenino">Femenino</option><option value="masculino">Masculino</option><option value="otro">Otro</option><option value="no_especificado">Prefiero no decir</option></select></label>
            <label><span>Direccion <small className="field-optional">(opcional)</small></span><textarea name="direccion" rows="3" value={datos.direccion || ''} onChange={actualizar} /></label>
            <label><span>Contacto adicional <small className="field-optional">(opcional)</small></span><textarea name="informacion_contacto" rows="3" placeholder="Ej.: telefono alternativo o correo secundario" value={datos.informacion_contacto || ''} onChange={actualizar} /></label>
            <label><span>Tipo de sangre <small className="field-optional">(opcional)</small></span><select name="tipo_sangre" value={datos.tipo_sangre || ''} onChange={actualizar}><option value="">Sin registrar</option><option>A+</option><option>A-</option><option>B+</option><option>B-</option><option>AB+</option><option>AB-</option><option>O+</option><option>O-</option></select><small className="field-help">Registralo solo si fue verificado clinicamente.</small></label>
            <label><span>Contacto de emergencia <small className="field-optional">(opcional)</small></span><input name="contacto_emergencia" maxLength={120} placeholder="Nombre de familiar o persona de confianza" value={datos.contacto_emergencia || ''} onChange={actualizar} /></label>
            <label><span>Telefono de emergencia <small className="field-optional">(opcional)</small></span><input name="telefono_emergencia" type="tel" maxLength={20} placeholder="Numero al que se puede llamar" value={datos.telefono_emergencia || ''} onChange={actualizar} /></label>
          </div>
        </section>}

        {error && <p className="form-error" role="alert">{error}</p>}
        <div className="account-form-actions"><button className="secondary-button" type="button" onClick={onCancel}>Cancelar</button><button className="primary-button" type="submit" disabled={procesando}>{procesando ? 'Guardando...' : esEdicion ? 'Guardar cambios' : 'Crear cuenta'}</button></div>
      </form>
    </section>
  );
}
