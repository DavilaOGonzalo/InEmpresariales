from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    initial = True

    dependencies = [('usuarios', '0009_hospital')]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='Hospital',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('nombre', models.CharField(max_length=150)),
                        ('direccion', models.CharField(max_length=255)),
                        ('contacto', models.CharField(max_length=100)),
                    ],
                    options={
                        'db_table': 'usuarios_hospital',
                        'ordering': ['nombre'],
                        'constraints': [models.UniqueConstraint(Lower('nombre'), name='uniq_hospital_nombre_ci')],
                    },
                ),
            ],
        ),
    ]