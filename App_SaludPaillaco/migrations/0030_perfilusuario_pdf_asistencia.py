# Generated by Django 5.0 on 2025-01-26 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_SaludPaillaco', '0029_pdfdocumento'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilusuario',
            name='pdf_asistencia',
            field=models.FileField(blank=True, null=True, upload_to='perfil_usuario_pdfs/'),
        ),
    ]
