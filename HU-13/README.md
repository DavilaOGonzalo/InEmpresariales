# HU-12: estado de hospitales y servicios

Los hospitales y servicios nuevos se crean activos. El administrador puede consultar el estado en sus listas y activarlos o desactivarlos sin borrar sus datos ni sus asignaciones.

Para aplicar las migraciones, desde `HU-12/ESSAID` ejecuta:

```powershell
python manage.py migrate
```

La disponibilidad pública se consulta mediante `GET /api/disponibilidad/`. La respuesta incluye solo hospitales activos y, dentro de cada hospital, sus servicios activos asignados. Los selectores de asignación también excluyen los elementos inactivos y la API rechaza nuevas asignaciones que los incluyan.
