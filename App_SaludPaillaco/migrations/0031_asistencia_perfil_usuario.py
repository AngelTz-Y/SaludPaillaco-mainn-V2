# Generated by Django 5.0 on 2025-01-26 23:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_SaludPaillaco', '0030_perfilusuario_pdf_asistencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='asistencia',
            name='perfil_usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='App_SaludPaillaco.perfilusuario'),
        ),
    ]
