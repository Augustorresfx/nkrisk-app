# Generated by Django 4.2.6 on 2023-12-11 19:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_alter_tarifaflota_tasa'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehiculo',
            old_name='premio_anual',
            new_name='premio_con_iva',
        ),
        migrations.RenameField(
            model_name='vehiculo',
            old_name='premio_vigente',
            new_name='premio_sin_iva',
        ),
        migrations.RenameField(
            model_name='vehiculo',
            old_name='prima_anual',
            new_name='prima_pza',
        ),
        migrations.RenameField(
            model_name='vehiculo',
            old_name='prima_vigente',
            new_name='prima_tecnica',
        ),
    ]