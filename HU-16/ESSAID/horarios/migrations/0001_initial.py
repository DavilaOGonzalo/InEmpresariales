import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('usuarios', '0010_mover_hospitales_a_app'),
    ]

    operations = [
        migrations.CreateModel(
            name='HorarioMedico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(db_index=True)),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('intervalo_minutos', models.PositiveSmallIntegerField(default=30)),
                ('activo', models.BooleanField(db_index=True, default=True)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('medico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horarios', to='usuarios.medico')),
            ],
            options={
                'verbose_name': 'horario médico',
                'verbose_name_plural': 'horarios médicos',
                'db_table': 'horarios_medicos',
                'ordering': ['fecha', 'hora_inicio', 'medico_id'],
            },
        ),
        migrations.AddConstraint(
            model_name='horariomedico',
            constraint=models.UniqueConstraint(fields=('medico', 'fecha', 'hora_inicio', 'hora_fin'), name='horario_medico_unico_rango'),
        ),
    ]
