from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('hospitales', '0002_servicio_medico'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.PositiveIntegerField(null=True, unique=True, editable=False)),
                ('nombre', models.CharField(max_length=150)),
                ('descripcion', models.TextField(blank=True)),
            ],
            options={'ordering': ['numero']},
        ),
        migrations.CreateModel(
            name='HospitalServicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hospital', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relaciones_servicios', to='hospitales.hospital')),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relaciones_hospitales', to='servicios.servicio')),
            ],
            options={'ordering': ['hospital__nombre', 'servicio__numero']},
        ),
        migrations.AddConstraint(
            model_name='hospitalservicio',
            constraint=models.UniqueConstraint(fields=('hospital', 'servicio'), name='uniq_hospital_servicio'),
        ),
    ]