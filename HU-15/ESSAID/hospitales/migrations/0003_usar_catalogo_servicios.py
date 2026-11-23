from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('hospitales', '0002_servicio_medico'),
        ('servicios', '0002_catalogo_predeterminado'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='serviciomedico',
            name='uniq_servicio_hospital_nombre_ci',
        ),
        migrations.DeleteModel(name='ServicioMedico'),
        migrations.AddField(
            model_name='hospital',
            name='servicios',
            field=models.ManyToManyField(
                blank=True,
                related_name='hospitales',
                through='servicios.HospitalServicio',
                to='servicios.servicio',
            ),
        ),
    ]