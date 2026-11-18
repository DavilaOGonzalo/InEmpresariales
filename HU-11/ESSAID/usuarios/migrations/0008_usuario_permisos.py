from django.db import migrations, models


def asignar_permisos_iniciales(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    permisos_por_rol = {
        'medico': ['paciente.leer', 'paciente.editar', 'medico.leer_propio', 'medico.editar_propio'],
        'paciente': ['paciente.leer_propio', 'paciente.editar_propio', 'medico.leer'],
    }
    for rol, permisos in permisos_por_rol.items():
        Usuario.objects.filter(rol=rol).update(permisos=permisos)


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0007_medico_cmp_medico_direccion_medico_especialidad_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='permisos',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(asignar_permisos_iniciales, migrations.RunPython.noop),
    ]
