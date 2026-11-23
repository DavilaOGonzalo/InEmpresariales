from datetime import datetime, timedelta

from django.utils import timezone

from citas.models import Cita
from usuarios.models import Medico

from .models import HorarioMedico


def normalizar_nombre_medico(nombre):
    nombre = ' '.join(nombre.casefold().split())
    for titulo in ('dr. ', 'dra. ', 'doctor ', 'doctora '):
        if nombre.startswith(titulo):
            return nombre[len(titulo):].strip()
    return nombre


def buscar_espacios_libres(nombre_medico, fecha, excluir_cita_id=None, bloquear=False):
    perfiles = list(Medico.objects.select_related('usuario').all())
    perfiles = [
        medico for medico in perfiles
        if normalizar_nombre_medico(f'{medico.usuario.nombre} {medico.usuario.apellido}') == normalizar_nombre_medico(nombre_medico)
    ]
    if not perfiles:
        return None, set(), set(), 'No se encontró un perfil médico asociado a la cita.'
    if len(perfiles) > 1:
        return None, set(), set(), 'Hay más de un médico con ese nombre; no se puede verificar el horario con seguridad.'

    medico = perfiles[0]
    horarios = HorarioMedico.objects.filter(medico=medico, fecha=fecha, activo=True).order_by('hora_inicio')
    if bloquear:
        horarios = horarios.select_for_update()
    horarios = list(horarios)
    if not horarios:
        return medico, set(), set(), 'El médico no tiene un horario activo para esa fecha.'

    citas = Cita.objects.filter(fecha=fecha).exclude(estado=Cita.ESTADO_CANCELADA)
    if excluir_cita_id is not None:
        citas = citas.exclude(pk=excluir_cita_id)
    if bloquear:
        citas = citas.select_for_update()
    horas_ocupadas = [
        cita.hora for cita in citas
        if normalizar_nombre_medico(cita.medico) == normalizar_nombre_medico(nombre_medico)
    ]

    libres = set()
    programados = set()
    ahora = timezone.localtime().replace(tzinfo=None, second=0, microsecond=0)
    for horario in horarios:
        inicio = datetime.combine(fecha, horario.hora_inicio)
        fin = datetime.combine(fecha, horario.hora_fin)
        intervalo = timedelta(minutes=horario.intervalo_minutos)
        slot = inicio
        while slot + intervalo <= fin:
            inicio_slot = slot.time()
            fin_slot = (slot + intervalo).time()
            etiqueta = inicio_slot.strftime('%H:%M')
            programados.add(etiqueta)
            ocupado = any(inicio_slot <= hora < fin_slot for hora in horas_ocupadas)
            if slot > ahora and not ocupado:
                libres.add(etiqueta)
            slot += intervalo
    return medico, programados, libres, None


def validar_espacio_libre(nombre_medico, fecha, hora, excluir_cita_id=None, bloquear=False):
    medico, programados, libres, error = buscar_espacios_libres(
        nombre_medico,
        fecha,
        excluir_cita_id=excluir_cita_id,
        bloquear=bloquear,
    )
    if error:
        return medico, error
    if hora not in programados:
        return medico, 'La hora seleccionada no coincide con un espacio del horario activo del médico.'
    if hora not in libres:
        return medico, 'Ese horario ya está ocupado o ya pasó. Selecciona otro espacio disponible.'
    return medico, None
