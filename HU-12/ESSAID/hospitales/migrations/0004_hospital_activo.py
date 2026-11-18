from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('hospitales', '0003_usar_catalogo_servicios')]

    operations = [
        migrations.AddField(
            model_name='hospital',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]
