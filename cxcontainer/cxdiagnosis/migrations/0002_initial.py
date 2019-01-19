from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def create_domains(apps, schema_editor):
    Domain = apps.get_model('cxdiagnosis', 'Domain')
    Domain.objects.create(name='H & PS')
    Domain.objects.create(name='Insurance')
    Domain.objects.create(name='Travel')
    Domain.objects.create(name='Banking')
    Domain.objects.create(name='Energy')
    Domain.objects.create(name='Finance')
    Domain.objects.create(name='Retail')

def create_organisations(apps, schema_editor):
    Organisation = apps.get_model('cxdiagnosis', 'Organisation')
    Organisation.objects.create(name='abc pvt ltd')
    Organisation.objects.create(name='xyz pft ltd')
    Organisation.objects.create(name='pqr ltd')
    Organisation.objects.create(name='demo ltd')

class Migration(migrations.Migration):

    dependencies = [
        ('cxdiagnosis', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_domains),
        migrations.RunPython(create_organisations),
    ]
