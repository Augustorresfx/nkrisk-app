# Generated by Django 4.2.6 on 2024-06-10 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_rename_porcentaje_diferencia_movimiento_premio_con_iva_porcentaje_diferencia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='iibb',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True),
        ),
    ]
