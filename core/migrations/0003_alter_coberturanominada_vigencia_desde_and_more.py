# Generated by Django 4.2.6 on 2024-12-03 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rename_estadoactual_coberturainnominada_estadoconsulta_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coberturanominada',
            name='vigencia_desde',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coberturanominada',
            name='vigencia_hasta',
            field=models.DateField(blank=True, null=True),
        ),
    ]
