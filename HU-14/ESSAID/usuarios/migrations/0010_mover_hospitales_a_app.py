from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0009_hospital'),
        ('hospitales', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[migrations.DeleteModel(name='Hospital')],
        ),
    ]