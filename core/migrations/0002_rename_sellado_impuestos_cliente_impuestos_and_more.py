# Generated by Django 4.2.6 on 2024-02-19 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cliente',
            old_name='sellado_impuestos',
            new_name='impuestos',
        ),
        migrations.AddField(
            model_name='cliente',
            name='sellados',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True),
        ),
    ]
