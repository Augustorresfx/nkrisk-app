# Generated by Django 4.2.6 on 2024-12-13 16:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_rename_codigoasegurado_coberturainnominada_codigo_asegurado_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coberturainnominada',
            old_name='codigo_asegurado',
            new_name='codigoAsegurado',
        ),
    ]
