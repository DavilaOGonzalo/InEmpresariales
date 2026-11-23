# HU-16: cancelación y reprogramación de citas

El administrador puede cancelar citas programadas o confirmadas, o cambiar su fecha y hora. Al reprogramar, el servidor comprueba que el espacio pertenezca a un horario activo del médico, que sea futuro y que ninguna otra cita vigente lo ocupe. La verificación y el guardado se realizan en una transacción para impedir reservas simultáneas del mismo espacio.

## Puesta en marcha

Desde `HU-16/ESSAID` ejecuta:

```powershell
python manage.py migrate
python manage.py runserver
```

El frontend se inicia desde `HU-16/ESSAID/frontend` con `npm install` y `npm run dev`.

## Administración

En **Citas**, el administrador puede elegir **Reprogramar** para seleccionar fecha y uno de los espacios libres del médico, o **Cancelar** para liberar la hora. La API administrativa conserva `GET /api/admin/citas/` y actualiza una cita con `PATCH /api/admin/citas/<id>/`.

Para cancelar, envía `{"accion":"cancelar"}`. Para reprogramar, envía `{"fecha":"AAAA-MM-DD","hora":"HH:MM"}`. Solo las citas programadas y confirmadas pueden cancelarse o moverse; las completadas y canceladas son finales. Si la fecha/hora no pertenece a un horario activo, está en el pasado o ya está ocupada, la API responde con un error y conserva los datos actuales.

## Horarios para pacientes

Los rangos se administran desde **Horarios médicos**. La página pública `/horarios-disponibles` y la API `GET /api/horarios-disponibles/?fecha=AAAA-MM-DD` presentan solo espacios futuros libres. Se puede limitar la consulta con `medico_id=<id>`.
