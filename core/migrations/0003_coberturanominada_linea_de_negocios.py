# Generated by Django 4.2.6 on 2024-06-28 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_coberturainnominada_coberturanominada'),
    ]

    operations = [
        migrations.AddField(
            model_name='coberturanominada',
            name='linea_de_negocios',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
