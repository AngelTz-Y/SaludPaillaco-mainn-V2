from django.db import models
from django.contrib.auth.models import User

class Profesion_Oficio(models.Model):
    profesion_oficio = models.CharField(max_length=100)

    def __str__(self):
        return self.profesion_oficio

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12)
    telefono = models.CharField(max_length=15)
    profesion = models.ForeignKey(Profesion_Oficio, on_delete=models.SET_NULL, null=True)
    aprobado = models.BooleanField(default=False)
    numero_espera = models.PositiveIntegerField(null=True, blank=True)  # Número secuencial

    def __str__(self):
        return self.user.username



class AsistenciaPDF(models.Model):
    perfil_usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='asistencias_pdfs', null=True, blank=True)
    rut_usuario = models.CharField(max_length=12, null=True, blank=True)  # Campo opcional para rut en caso de no estar registrado
    archivo_pdf = models.FileField(upload_to='asistencias_pdfs/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    mes_asistencia = models.CharField(max_length=20, null=True, blank=True)
    ano_asistencia = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"PDF de {self.rut_usuario or self.perfil_usuario.rut} - {self.fecha_subida}"




class Asistencia(models.Model):
    ac = models.CharField(max_length=100)  # Elimina el `unique=True` para permitir duplicados de `ac`
    rut = models.CharField(max_length=12)  # El rut es de tipo cadena para almacenarlo correctamente.
    nombre = models.CharField(max_length=200)
    dpto = models.CharField(max_length=100)
    mes = models.CharField(max_length=20)
    ano = models.IntegerField()
    fecha = models.DateField()
    marcaciones = models.TextField()
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.rut} - {self.ac}"

    


