# Generated by Django 4.2.6 on 2024-05-23 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_movimiento_porcentaje_diferencia'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movimiento',
            old_name='porcentaje_diferencia',
            new_name='premio_con_iva_porcentaje_diferencia',
        ),
        migrations.AddField(
            model_name='movimiento',
            name='prima_pza_porcentaje_diferencia',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
