# Generated by Django 4.2.6 on 2024-12-13 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_coberturanominada_monto_temporal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coberturainnominada',
            old_name='codigoAsegurado',
            new_name='codigo_asegurado',
        ),
        migrations.RenameField(
            model_name='coberturainnominada',
            old_name='estadoConsulta',
            new_name='estado_actual',
        ),
        migrations.RenameField(
            model_name='coberturainnominada',
            old_name='fecha_consulta',
            new_name='fecha_primer_consulta',
        ),
        migrations.AddField(
            model_name='coberturainnominada',
            name='codigo_autorizacion',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='coberturainnominada',
            name='fecha_hasta',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='coberturainnominada',
            name='fecha_ultima_consulta',
            field=models.DateField(blank=True, null=True),
        ),
    ]
