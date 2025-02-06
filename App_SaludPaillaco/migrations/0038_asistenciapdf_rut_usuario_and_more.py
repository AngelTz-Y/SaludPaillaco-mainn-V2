# Generated by Django 5.0 on 2025-02-06 14:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_SaludPaillaco', '0037_asistenciapdf_delete_registropdfasistencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='asistenciapdf',
            name='rut_usuario',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='asistenciapdf',
            name='perfil_usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asistencias_pdfs', to='App_SaludPaillaco.perfilusuario'),
        ),
    ]
