# Generated by Django 4.2.6 on 2024-06-28 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoberturaInnominada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_nacional', models.CharField(max_length=100)),
                ('nombre_cliente', models.CharField(max_length=100)),
                ('fecha_primer_consulta', models.DateTimeField(blank=True, null=True)),
                ('fecha_ultima_consulta', models.DateTimeField(blank=True, null=True)),
                ('codigoAutorizacion', models.CharField(max_length=100)),
                ('fecha_hasta', models.DateTimeField(blank=True, null=True)),
                ('codigoAsegurado', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CoberturaNominada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_nacional', models.CharField(max_length=100)),
                ('pais', models.CharField(max_length=25)),
                ('ciudad', models.CharField(max_length=100)),
                ('cliente', models.CharField(max_length=100)),
                ('vigencia_desde', models.DateTimeField(blank=True, null=True)),
                ('vigencia_hasta', models.DateTimeField(blank=True, null=True)),
                ('moneda', models.CharField(max_length=5)),
                ('monto_solicitado', models.IntegerField()),
                ('monto_aprobado', models.IntegerField()),
                ('estado', models.CharField(max_length=14)),
                ('condicion_de_venta', models.TextField()),
                ('plazo_en_dias', models.IntegerField()),
                ('codigoAsegurado', models.CharField(blank=True, max_length=100, null=True)),
                ('observaciones', models.TextField()),
            ],
        ),
    ]
