# Generated by Django 4.2.6 on 2024-07-03 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_aseguradocredito_fecha_vigencia_desde_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimiento',
            name='flota',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimientos', to='core.flota'),
        ),
    ]
