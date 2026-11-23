from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paciente', models.CharField(max_length=201)),
                ('medico', models.CharField(db_index=True, max_length=201)),
                ('fecha', models.DateField(db_index=True)),
                ('hora', models.TimeField()),
                ('estado', models.CharField(choices=[('programada', 'Programada'), ('confirmada', 'Confirmada'), ('completada', 'Completada'), ('cancelada', 'Cancelada')], db_index=True, default='programada', max_length=20)),
            ],
            options={
                'verbose_name': 'cita',
                'verbose_name_plural': 'citas',
                'db_table': 'citas',
                'ordering': ['fecha', 'hora', 'id'],
            },
        ),
    ]
