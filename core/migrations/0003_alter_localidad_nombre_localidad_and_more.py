# Generated by Django 4.2.6 on 2024-03-18 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rename_sellado_impuestos_cliente_impuestos_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localidad',
            name='nombre_localidad',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='localidad',
            name='nombre_provincia',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True),
        ),
    ]
