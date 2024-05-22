# Generated by Django 4.2.6 on 2024-05-22 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_localidad_nombre_localidad_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimiento',
            name='premio_con_iva_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True),
        ),
        migrations.AddField(
            model_name='movimiento',
            name='premio_sin_iva_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True),
        ),
        migrations.AddField(
            model_name='movimiento',
            name='prima_pza_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True),
        ),
        migrations.AddField(
            model_name='movimiento',
            name='prima_tec_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True),
        ),
    ]
