from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('servicios', '0002_catalogo_predeterminado')]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]
