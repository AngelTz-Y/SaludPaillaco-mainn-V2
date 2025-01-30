# Importaciones de Django (Incluido con Django, no requiere instalación adicional)
# Modelos y gestión de usuarios y grupos
from django.contrib.auth.models import User, Group

from reportlab.pdfgen import canvas

# Autenticación y gestión de sesiones de usuarios
from django.contrib.auth import authenticate, login

# Vistas y manejo de respuestas HTTP
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404

# Decoradores de seguridad para vistas que requieren autenticación
from django.contrib.auth.decorators import login_required

# Excepciones y validaciones
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File

# Configuración de ajustes de Django
from django.conf import settings

# Sistema de mensajes en Django
from django.contrib import messages

# Manejo de rutas de archivos
import os

# Importaciones para manejo de modelos personalizados (Incluido en tu proyecto)
from .models import *  # Importa todos los modelos definidos en el archivo 'models.py'

# Importaciones para manejo de archivos Excel con openpyxl
from .forms import ExcelUploadForm  # Formulario para cargar archivos Excel
from openpyxl.styles import *  # Herramientas para dar formato a celdas de Excel

# Creación y manipulación de PDFs
from xhtml2pdf import pisa  # Generador de PDFs desde HTML, asegurarse de instalar esta librería
import base64  # Codificación y decodificación de datos en base64
import os  # Manejo de rutas y directorios
from datetime import datetime  # Manejo de fechas y horas
from PyPDF2 import PdfReader  # Herramienta para leer y manipular PDFs
import pdfplumber  # Herramienta para extraer texto e imágenes de PDFs

# Manejo de configuraciones y rutas en Django
import re  # Expresiones regulares para validaciones o manipulaciones de texto

# Importación de pandas para manejo de datos en estructuras tabulares
import pandas as pd  # Herramienta poderosa para el análisis de datos

# Importaciones para manejo de la vista y los formularios relacionados con 'Asistencia'
from .models import Asistencia  # Modelo 'Asistencia' para manipular datos de asistencia de empleados
from .forms import AsistenciaForm  # Formulario para ingresar o actualizar datos de asistencia
from django.core.exceptions import ValidationError  # Excepciones para validaciones personalizadas

# Manipulación de PDFs, para leer y modificar documentos
import PyPDF2  # Herramienta para trabajar con PDFs, como leer metadatos, fusionar, etc.
from io import BytesIO  # Manejo de datos binarios en memoria (necesario para PDFs)



# Create your views here.
def inicio(request):
    if request.method == 'POST':
        # Procesar el formulario de inicio de sesión
        rut = request.POST.get('rut', '').strip()
        password = request.POST.get('password', '').lower().strip()

        try:
            # Buscar al usuario por el RUT
            perfil = PerfilUsuario.objects.get(rut=rut)
            user = perfil.user  # Obtener el usuario relacionado

            # Autenticar al usuario con la contraseña
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)

                # Verificar si el usuario es administrador (staff)
                if user.is_staff:
                    # Si es administrador, redirigir al panel de administración
                    return redirect('panel_administrador')

                # Verificar si el usuario pertenece al grupo "usuario en espera"
                if user.groups.filter(name='usuario en espera').exists():
                    # Calcular la posición en la lista de espera
                    usuarios_en_espera = PerfilUsuario.objects.filter(aprobado=False).order_by('numero_espera')
                    posicion = list(usuarios_en_espera).index(perfil) + 1

                    # Renderizar la interfaz para usuarios en espera con su posición
                    return render(request, 'Grupos/Usuarios/usuario_no_registrado.html', {
                        'posicion': posicion,
                        'total_espera': usuarios_en_espera.count(),
                        'numero_espera': perfil.numero_espera
                    })
                
                # Verificar si el usuario pertenece al grupo "usuario registrado"
                if user.groups.filter(name='usuario registrado').exists():
                    return render(request, 'Grupos/Usuarios/usuario_registrado.html')
                
                # Si no pertenece a ningún grupo, redirigir con un mensaje de error
                return render(request, 'inicio.html', {'error': 'No tiene permisos para acceder a esta sección.'})
            else:
                return render(request, 'inicio.html', {'error': 'Credenciales incorrectas.'})

        except PerfilUsuario.DoesNotExist:
            return render(request, 'inicio.html', {'error': 'El RUT ingresado no está registrado.'})

    # Si la solicitud es GET, mostrar la página de inicio de sesión
    return render(request, 'inicio.html')


def registrarse(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        firstname = request.POST.get('firstname', '').strip()
        lastname = request.POST.get('lastname', '').strip()
        username = f"{firstname} {lastname}"  # Nombre completo
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm-password', '').strip()
        rut = request.POST.get('rut', '').strip()
        telefono = request.POST.get('phone', '').strip()
        profesion_id = request.POST.get('profession', '').strip()

        # Verificar que las contraseñas coinciden
        if password != confirm_password:
            return render(request, 'registrarse.html', {'error': 'Las contraseñas no coinciden.'})

        # Verificar que la profesión seleccionada existe
        try:
            profesion = Profesion_Oficio.objects.get(id=profesion_id)
        except Profesion_Oficio.DoesNotExist:
            return render(request, 'registrarse.html', {'error': 'La profesión seleccionada no es válida.'})

        # Crear el usuario en Django
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=firstname,
                last_name=lastname
            )
        except Exception as e:
            return render(request, 'registrarse.html', {'error': f'Error al crear el usuario: {e}'})

        # Asignar el rol de "usuario en espera"
        group, created = Group.objects.get_or_create(name='usuario en espera')
        user.groups.add(group)

        # Generar número de espera
        numero_espera = PerfilUsuario.objects.filter(aprobado=False).count() + 1

        # Crear el perfil del usuario
        try:
            perfil = PerfilUsuario(
                user=user,
                rut=rut,
                telefono=telefono,
                profesion=profesion,
                aprobado=False,
                numero_espera=numero_espera
            )
            perfil.save()
        except Exception as e:
            user.delete()  # Eliminar usuario si el perfil no se pudo crear
            return render(request, 'registrarse.html', {'error': f'Error al crear el perfil: {e}'})

        # Mostrar el número de espera al usuario (opcional: redirigir con mensaje)
        return render(request, 'registro_exitoso.html', {'numero_espera': numero_espera})

    else:
        profesiones = Profesion_Oficio.objects.all()
        return render(request, 'registrarse.html', {'profesiones': profesiones})


        
        
def registro_exitoso(request):
    return render(request, 'registro_exitoso.html')



def aceptacion_usuario(request):
    if not request.user.is_staff:  # Verificar si el usuario tiene privilegios de administrador
        return redirect('inicio')  # Redirigir a la página de inicio si no es administrador

    # Obtener todos los usuarios en espera
    usuarios_en_espera = PerfilUsuario.objects.filter(aprobado=False)

    if request.method == 'POST':
        # Obtener el RUT del usuario que se va a aceptar
        rut_aceptado = request.POST.get('rut_aceptado', '').strip()

        try:
            # Buscar al usuario en espera por su RUT
            perfil_usuario = PerfilUsuario.objects.get(rut=rut_aceptado, aprobado=False)
            
            # Obtener el usuario asociado al perfil
            user = perfil_usuario.user

            # Verificar si el usuario está en el grupo 'usuario en espera'
            grupo_espera = Group.objects.get(name='usuario en espera')
            if grupo_espera in user.groups.all():
                # Remover al usuario del grupo 'usuario en espera'
                user.groups.remove(grupo_espera)

                # Añadir al usuario al grupo 'usuario registrado'
                grupo_registrado, created = Group.objects.get_or_create(name='usuario registrado')
                user.groups.add(grupo_registrado)

                # Marcar al perfil como aprobado
                perfil_usuario.aprobado = True
                perfil_usuario.save()

                # Redirigir o mostrar un mensaje de éxito
                return redirect('aceptacion_usuario')  # Redirigir a la misma página para que se vea la actualización
            else:
                return render(request, 'aceptacion_usuario.html', {'error': 'El usuario no está en espera.'})

        except PerfilUsuario.DoesNotExist:
            return render(request, 'aceptacion_usuario.html', {'error': 'Usuario no encontrado en espera.'})

    return render(request, 'aceptacion_usuario.html', {'usuarios_en_espera': usuarios_en_espera})





def panel_administrador(request):
    return render(request, 'Grupos/Administrador/panel_administrador.html')


import openpyxl
from django.shortcuts import render
from .models import Asistencia
from django.http import HttpResponse
import datetime

from django.shortcuts import render
from .forms import ExcelUploadForm
from .models import Asistencia
import pandas as pd
from datetime import datetime

def cargar_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        # Leer el archivo Excel usando pandas
        df = pd.read_excel(excel_file)

        # Crear una lista para almacenar las instancias de Asistencia antes de guardarlas
        asistencia_list = []

        # Recorrer las filas del DataFrame y guardar los datos en la base de datos
        for index, row in df.iterrows():
            try:
                # Convertir la fecha al formato adecuado YYYY-MM-DD si no está vacía
                if pd.notna(row['fecha']):
                    try:
                        fecha = datetime.strptime(row['fecha'], '%d-%m-%Y').date()
                    except ValueError:
                        fecha = None  # Si la fecha tiene un formato incorrecto, asignamos None
                else:
                    fecha = None  # Si la fecha está vacía, la dejamos vacía

                # Verificar si cada campo está vacío y dejarlo vacío si es necesario
                ac = row['ac'] if pd.notna(row['ac']) else None
                rut = row['rut'] if pd.notna(row['rut']) else None  # Asegurarse de que el RUT no esté vacío
                nombre = row['nombre'] if pd.notna(row['nombre']) else ''
                dpto = row['dpto'] if pd.notna(row['dpto']) else ''
                mes = row['mes'] if pd.notna(row['mes']) else ''
                ano = row['ano'] if pd.notna(row['ano']) else ''
                marcaciones = row['marcaciones'] if pd.notna(row['marcaciones']) else ''
                observaciones = row['observaciones'] if pd.notna(row['observaciones']) else ''

                # Validación: Si el RUT es obligatorio, comprobamos si está vacío
                if not rut:
                    print(f"Fila {index}: El RUT está vacío, asociando los datos al AC {ac}.")
                    # Si no hay RUT, pero sí hay AC, buscamos el registro con el AC
                    if ac:
                        # Aquí puedes decidir cómo asociar el AC a un registro existente o crear uno nuevo
                        asistencia = Asistencia(
                            ac=ac,  # Asociar el valor de AC si el RUT no existe
                            rut=None,  # Si no hay RUT, dejamos este campo en blanco o como None
                            nombre=nombre,
                            dpto=dpto,
                            mes=mes,
                            ano=ano,
                            fecha=fecha,
                            marcaciones=marcaciones,
                            observaciones=observaciones,
                        )
                        asistencia_list.append(asistencia)
                    else:
                        print(f"Fila {index}: El RUT y el AC están vacíos, saltando esta fila.")
                        continue  # Si tampoco hay AC, omitimos la fila
                else:
                    # Si el RUT existe, asociamos los datos al RUT existente
                    asistencia = Asistencia(
                        ac=ac,  # Asociar AC si está presente
                        rut=rut,  # Asociamos el RUT
                        nombre=nombre,
                        dpto=dpto,
                        mes=mes,
                        ano=ano,
                        fecha=fecha,
                        marcaciones=marcaciones,
                        observaciones=observaciones,
                    )
                    asistencia_list.append(asistencia)  # Añadir la instancia a la lista

            except Exception as e:
                print(f"Error al procesar la fila {index}: {e}")

        # Guardar todas las instancias de una sola vez en la base de datos
        if asistencia_list:
            Asistencia.objects.bulk_create(asistencia_list)
            print(f"{len(asistencia_list)} registros guardados correctamente.")
        
        return render(request, 'cargar_excel.html', {'form': ExcelUploadForm(), 'asistencias': asistencia_list})

    # Si el método no es POST o no se cargó el archivo
    form = ExcelUploadForm()
    return render(request, 'cargar_excel.html', {'form': form})



from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import Asistencia

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import Asistencia

from datetime import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import Asistencia

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from datetime import datetime
from .models import Asistencia

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from datetime import datetime
from .models import Asistencia

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from datetime import datetime
from .models import Asistencia

def generar_pdf(request):
    # Obtener todos los registros de asistencia
    asistencias = Asistencia.objects.all()

    # Obtener la fecha y hora actual
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    hora_emision = datetime.now().strftime('%H:%M:%S')

    # Crear un diccionario para almacenar los registros por funcionario
    funcionarios = {}

    # Agrupar las asistencias por RUT (funcionario)
    for asistencia in asistencias:
        if asistencia.rut not in funcionarios:
            funcionarios[asistencia.rut] = {
                'nombre': asistencia.nombre,
                'rut': asistencia.rut,
                'departamento': asistencia.dpto,
                'asistencias': []
            }
        funcionarios[asistencia.rut]['asistencias'].append(asistencia)

    # Crear PDFs individuales para cada funcionario
    for rut, datos_funcionario in funcionarios.items():
        registros = datos_funcionario['asistencias']
        
        # Filtrar registros duplicados por fecha (eliminamos entradas con la misma fecha)
        registros_unicos = []
        fechas_vistas = set()
        for asistencia in registros:
            if asistencia.fecha not in fechas_vistas:
                registros_unicos.append(asistencia)
                fechas_vistas.add(asistencia.fecha)
        
        # Obtener el mes y año de los registros del funcionario (asumimos que todos los registros son del mismo mes/año)
        if registros_unicos:
            mes = registros_unicos[0].mes
            ano = registros_unicos[0].ano
        else:
            mes = ano = None  # En caso de no tener registros únicos, evitamos error

        # Crear el contenido HTML para el PDF usando una plantilla HTML
        html_content = render_to_string('generar_pdf.html', {
            'asistencias': registros_unicos,
            'fecha_actual': fecha_actual,
            'hora_emision': hora_emision,
            'mes': mes,
            'ano': ano,
            'nombre_funcionario': datos_funcionario['nombre'],
            'rut_funcionario': datos_funcionario['rut'],
            'departamento_funcionario': datos_funcionario['departamento'],
        })

        # Crear una respuesta HTTP con el tipo de contenido "application/pdf"
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="asistencia_{rut}.pdf"'

        # Convertir el HTML a PDF usando xhtml2pdf
        pisa_status = pisa.CreatePDF(html_content, dest=response)

        # Si ocurre un error al generar el PDF, mostrarlo
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=500)

        # Devolver el PDF generado como respuesta
        return response







def ver_pdf(request, asistencia_id):
    asistencia = Asistencia.objects.get(id=asistencia_id)
    return render(request, 'ver_pdf.html', {'asistencia': asistencia})






















