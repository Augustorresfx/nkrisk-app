# Generated by Django 4.2.6 on 2024-12-03 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_coberturanominada_vigencia_desde_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coberturanominada',
            name='vigencia_desde',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='coberturanominada',
            name='vigencia_hasta',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]