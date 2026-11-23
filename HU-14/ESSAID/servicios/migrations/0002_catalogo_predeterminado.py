from django.db import migrations, models
from django.db.models.functions import Lower


SERVICIOS_PREDETERMINADOS = [
    ('Medicina General', 'Atención médica integral para evaluar, diagnosticar y tratar enfermedades comunes.'),
    ('Cardiología', 'Diagnóstico, prevención y tratamiento de enfermedades del corazón y del sistema circulatorio.'),
    ('Pediatría', 'Atención médica especializada para recién nacidos, niños y adolescentes.'),
    ('Ginecología', 'Atención integral de la salud reproductiva y prevención de enfermedades del sistema femenino.'),
    ('Traumatología', 'Diagnóstico y tratamiento de lesiones y enfermedades de los huesos, articulaciones y músculos.'),
    ('Dermatología', 'Evaluación y tratamiento de enfermedades de la piel, cabello y uñas.'),
    ('Oftalmología', 'Evaluación de la visión y tratamiento de enfermedades oculares.'),
    ('Neurología', 'Diagnóstico y tratamiento de enfermedades del cerebro, médula espinal y sistema nervioso.'),
    ('Cirugía General', 'Atención quirúrgica para tratar enfermedades y lesiones que requieren intervención.'),
    ('Medicina Interna', 'Diagnóstico y tratamiento integral de enfermedades que afectan a los órganos internos.'),
]


def migrar_servicios_existentes(apps, schema_editor):
    ServicioViejo = apps.get_model('hospitales', 'ServicioMedico')
    Servicio = apps.get_model('servicios', 'Servicio')
    HospitalServicio = apps.get_model('servicios', 'HospitalServicio')
    db = schema_editor.connection.alias

    for numero, (nombre, descripcion) in enumerate(SERVICIOS_PREDETERMINADOS, start=1):
        Servicio.objects.using(db).create(numero=numero, nombre=nombre, descripcion=descripcion)

    siguientes = len(SERVICIOS_PREDETERMINADOS) + 1
    for anterior in ServicioViejo.objects.using(db).all().order_by('id'):
        actual = Servicio.objects.using(db).filter(nombre__iexact=anterior.nombre).first()
        if actual is None:
            actual = Servicio.objects.using(db).create(
                numero=siguientes,
                nombre=anterior.nombre,
                descripcion=anterior.descripcion or '',
            )
            siguientes += 1
        elif not actual.descripcion and anterior.descripcion:
            actual.descripcion = anterior.descripcion
            actual.save(using=db, update_fields=['descripcion'])

        HospitalServicio.objects.using(db).get_or_create(
            hospital_id=anterior.hospital_id,
            servicio_id=actual.pk,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('hospitales', '0002_servicio_medico'),
        ('servicios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrar_servicios_existentes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='servicio',
            name='numero',
            field=models.PositiveIntegerField(editable=False, unique=True),
        ),
        migrations.AddConstraint(
            model_name='servicio',
            constraint=models.UniqueConstraint(Lower('nombre'), name='uniq_servicio_nombre_ci'),
        ),
    ]