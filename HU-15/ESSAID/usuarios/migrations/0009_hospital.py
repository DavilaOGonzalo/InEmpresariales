from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [('usuarios', '0008_usuario_permisos')]

    operations = [
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('direccion', models.CharField(max_length=255)),
                ('contacto', models.CharField(max_length=100)),
            ],
            options={'ordering': ['nombre']},
        ),
        migrations.AddConstraint(
            model_name='hospital',
            constraint=models.UniqueConstraint(Lower('nombre'), name='uniq_hospital_nombre_ci'),
        ),
    ]
