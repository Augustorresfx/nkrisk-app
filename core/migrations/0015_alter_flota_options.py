# Generated by Django 4.2.6 on 2023-11-06 22:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_flota_created_vehiculo_created'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='flota',
            options={'ordering': ('created',), 'verbose_name_plural': 'Flotas'},
        ),
    ]