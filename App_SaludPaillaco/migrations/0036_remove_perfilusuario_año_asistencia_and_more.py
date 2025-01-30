# Generated by Django 5.0 on 2025-01-28 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_SaludPaillaco', '0035_registropdfasistencia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perfilusuario',
            name='año_asistencia',
        ),
        migrations.RemoveField(
            model_name='perfilusuario',
            name='mes_asistencia',
        ),
        migrations.RemoveField(
            model_name='perfilusuario',
            name='pdf_asistencia',
        ),
        migrations.AddField(
            model_name='registropdfasistencia',
            name='año_asistencia',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registropdfasistencia',
            name='mes_asistencia',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
