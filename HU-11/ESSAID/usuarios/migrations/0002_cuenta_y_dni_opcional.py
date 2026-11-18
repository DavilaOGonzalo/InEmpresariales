from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='cuenta',
            field=models.OneToOneField(
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='perfil_hospital',
                null=True,
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name='usuario',
            name='dni',
            field=models.CharField(max_length=20, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='correo',
            field=models.EmailField(max_length=254, blank=True, null=True, unique=True),
        ),
    ]
