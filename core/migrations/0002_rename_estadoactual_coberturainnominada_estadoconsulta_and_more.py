# Generated by Django 4.2.6 on 2024-10-23 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coberturainnominada',
            old_name='estadoActual',
            new_name='estadoConsulta',
        ),
        migrations.RenameField(
            model_name='coberturainnominada',
            old_name='fecha_hasta',
            new_name='fecha_consulta',
        ),
        migrations.RemoveField(
            model_name='coberturainnominada',
            name='codigoAutorizacion',
        ),
        migrations.RemoveField(
            model_name='coberturainnominada',
            name='fecha_primer_consulta',
        ),
        migrations.RemoveField(
            model_name='coberturainnominada',
            name='fecha_ultima_consulta',
        ),
    ]