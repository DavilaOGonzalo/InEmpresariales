# HU-14: consulta y cambio de estado de citas

El administrador puede consultar las citas registradas en la tabla `citas`, filtrarlas por fecha, médico o estado y actualizar el estado desde la lista. La app `citas` utiliza el ORM de Django para leer y guardar esa tabla; el paciente y el médico se guardan como nombres en cada cita.

Para crear la tabla, desde `HU-13/ESSAID` ejecuta:

```powershell
python manage.py migrate
```

Las citas se pueden registrar desde el panel Django en `/admin/citas/cita/add/`. La consulta del frontend está disponible en el menú **Citas** y usa `GET /api/admin/citas/`, con filtros opcionales `fecha`, `medico` y `estado`.

El estado se cambia con `POST /api/admin/citas/<id>/estado/`, enviando `{"estado":"confirmada"}`. Las transiciones permitidas son `programada` a `confirmada` o `cancelada`, y `confirmada` a `completada` o `cancelada`. Los estados `completada` y `cancelada` son finales. El servidor valida cada cambio, requiere sesión de administrador y devuelve la cita actualizada.
