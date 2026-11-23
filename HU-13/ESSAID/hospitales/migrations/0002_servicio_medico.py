from django.db import migrations, models
import django.db.models.deletion
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [
        ('hospitales', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServicioMedico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('descripcion', models.TextField(blank=True)),
                ('hospital', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicios', to='hospitales.hospital')),
            ],
            options={'ordering': ['hospital__nombre', 'nombre']},
        ),
        migrations.AddConstraint(
            model_name='serviciomedico',
            constraint=models.UniqueConstraint(Lower('nombre'), 'hospital', name='uniq_servicio_hospital_nombre_ci'),
        ),
    ]