# HU-13: consulta de citas

El administrador puede consultar las citas registradas en la tabla `citas` y filtrarlas por fecha, médico o estado. La app `citas` utiliza el ORM de Django para leer esa tabla; el paciente y el médico se guardan como nombres en cada cita.

Para crear la tabla, desde `HU-13/ESSAID` ejecuta:

```powershell
python manage.py migrate
```

Las citas se pueden registrar desde el panel Django en `/admin/citas/cita/add/`. La consulta del frontend está disponible en el menú **Citas** y usa `GET /api/admin/citas/`, con filtros opcionales `fecha`, `medico` y `estado`.
