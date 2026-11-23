# HU-15: horarios disponibles de médicos

El administrador puede registrar, modificar, activar y desactivar rangos de atención por médico y fecha desde **Horarios médicos**. Cada rango se divide en espacios con duración configurable de 5 a 240 minutos. Se rechazan rangos duplicados o solapados para el mismo médico y fecha.

## Puesta en marcha

Desde `HU-15/ESSAID` ejecuta:

```powershell
python manage.py migrate
python manage.py runserver
```

El frontend se inicia desde `HU-15/ESSAID/frontend` con `npm install` y `npm run dev`.

## Administración

El menú **Horarios médicos** requiere una sesión de superusuario. La API `GET /api/admin/horarios/` devuelve los horarios, los médicos y el conteo de espacios libres y ocupados. Se crea un rango con `POST /api/admin/horarios/` y se actualiza con `PATCH /api/admin/horarios/<id>/`. El cuerpo acepta `medico_id`, `fecha` (`AAAA-MM-DD`), `hora_inicio`, `hora_fin`, `intervalo_minutos` y, para activar o desactivar, `activo`.

Los rangos se expresan para una fecha concreta; el final debe ser posterior al inicio y su duración debe dividirse exactamente entre los intervalos. Un horario activo no puede cruzarse con otro horario activo del mismo médico. Las citas programadas, confirmadas o completadas ocupan el espacio donde comienzan; las canceladas lo liberan.

## Consulta para pacientes

La página pública `/horarios-disponibles` permite consultar un día sin iniciar sesión. La API pública `GET /api/horarios-disponibles/?fecha=AAAA-MM-DD` devuelve únicamente espacios futuros de horarios activos que no estén ocupados. Puede limitarse a un médico agregando `medico_id=<id>`. Las fechas pasadas no se aceptan.
