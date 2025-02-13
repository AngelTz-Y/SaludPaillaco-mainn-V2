# Generated by Django 5.0 on 2025-01-23 01:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_SaludPaillaco', '0011_delete_registrocambios'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asistencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('horas_trabajadas', models.DecimalField(decimal_places=2, max_digits=5)),
                ('perfil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_SaludPaillaco.perfilusuario')),
            ],
        ),
    ]
