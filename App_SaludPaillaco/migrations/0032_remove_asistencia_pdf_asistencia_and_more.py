# Generated by Django 5.0 on 2025-01-27 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_SaludPaillaco', '0031_asistencia_perfil_usuario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asistencia',
            name='pdf_asistencia',
        ),
        migrations.RemoveField(
            model_name='asistencia',
            name='perfil_usuario',
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='año_asistencia',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='mes_asistencia',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
