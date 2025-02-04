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
from django.views.decorators.csrf import csrf_protect

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



@csrf_protect
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
                    return redirect('usuario_registrado')
                
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





@csrf_protect
def panel_administrador(request):
    return render(request, 'Grupos/Administrador/panel_administrador.html')

@csrf_protect
def panel_UsuarioRegistrado(request):
    return render(request, 'Grupos/Usuarios/usuario_registrado.html')

@csrf_protect
def panel_UsuarioNoRegistrado(request):
    return render(request, 'Grupos/Usuarios/usuario_no_registrado.html')


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
        
        # Generar el PDF para cada funcionario después de guardar los registros
        for asistencia in asistencia_list:
            generar_pdf(asistencia.rut)

        return render(request, 'cargar_excel.html', {'form': ExcelUploadForm(), 'asistencias': asistencia_list})

    # Si el método no es POST o no se cargó el archivo
    form = ExcelUploadForm()
    return render(request, 'cargar_excel.html', {'form': form})





import locale
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import Asistencia

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.timezone import now
from xhtml2pdf import pisa
import os
from datetime import datetime

from datetime import datetime

from datetime import datetime

def generar_pdf(request):
    asistencias = Asistencia.objects.all()
    fecha_actual = datetime.now().strftime('%d/%m/%Y')

    dias_semana = {'mon': 'Lun', 'tue': 'Mar', 'wed': 'Mie', 'thu': 'Jue', 'fri': 'Vie', 'sat': 'Sab', 'sun': 'Dom'}
    funcionarios = {}

    # Organiza las asistencias por rut, mes y año
    for asistencia in asistencias:
        clave = (asistencia.rut, asistencia.mes, asistencia.ano)
        if clave not in funcionarios:
            funcionarios[clave] = {
                'nombre': asistencia.nombre,
                'rut': asistencia.rut,
                'departamento': asistencia.dpto,
                'mes': asistencia.mes,
                'ano': asistencia.ano,
                'asistencias': []
            }
        dia_abreviado = asistencia.fecha.strftime('%a').lower().replace('.', '')
        asistencia.dia_semana = dias_semana.get(dia_abreviado, asistencia.fecha.strftime('%a'))
        funcionarios[clave]['asistencias'].append(asistencia)

    # Crear el directorio principal de PDFs
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'asistencias_pdfs')
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    for clave, datos_funcionario in funcionarios.items():
        rut, mes, ano = clave
        registros = datos_funcionario['asistencias']

        # Asegúrate de que hay registros de asistencia antes de continuar
        if not registros:
            continue

        # Eliminar registros duplicados
        registros_unicos = []
        fechas_vistas = set()
        for asistencia in registros:
            if asistencia.fecha not in fechas_vistas:
                registros_unicos.append(asistencia)
                fechas_vistas.add(asistencia.fecha)

        # Verificar si el PDF ya fue generado para este funcionario y mes/año
        if AsistenciaPDF.objects.filter(perfil_usuario__rut=rut, mes_asistencia=mes, ano_asistencia=ano).exists():
            continue

        # Verificar si el perfil de usuario existe
        try:
            perfil_usuario = PerfilUsuario.objects.get(rut=rut)
        except PerfilUsuario.DoesNotExist:
            # Si no se encuentra el perfil, se salta la generación de PDF para este rut
            continue

        # Ahora se genera la hora exacta en base al momento de la solicitud
        hora_emision = datetime.now().strftime('%H:%M:%S')

        # Generar el contenido HTML del PDF
        html_content = render_to_string('generar_pdf.html', {
            'asistencias': registros_unicos,
            'fecha_actual': fecha_actual,
            'hora_emision': hora_emision,  # Genera la hora actual en cada solicitud
            'mes': mes,
            'ano': ano,
            'nombre_funcionario': datos_funcionario['nombre'],
            'rut_funcionario': datos_funcionario['rut'],
            'departamento_funcionario': datos_funcionario['departamento'],
        })

        # Crear directorio para mes y año dentro de la carpeta 'asistencias_pdfs'
        mes_ano_dir = os.path.join(pdf_dir, str(mes), str(ano))
        if not os.path.exists(mes_ano_dir):
            os.makedirs(mes_ano_dir)

        # Modificar el nombre del archivo PDF
        pdf_filename = f'{datos_funcionario["nombre"]}_{mes}_{ano}.pdf'
        pdf_path = os.path.join(mes_ano_dir, pdf_filename)

        # Crear el PDF
        with open(pdf_path, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

        # Asociar el PDF generado con el perfil de usuario
        AsistenciaPDF.objects.create(
            perfil_usuario=perfil_usuario,
            archivo_pdf=os.path.join('asistencias_pdfs', str(mes), str(ano), pdf_filename),
            mes_asistencia=mes,
            ano_asistencia=ano
        )
    
    return HttpResponse("PDFs generados y asociados correctamente, si corresponde.")






from django.http import FileResponse
from django.shortcuts import render
from .models import AsistenciaPDF

from django.shortcuts import render
from django.http import FileResponse
from App_SaludPaillaco.models import AsistenciaPDF


from django.shortcuts import render
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from App_SaludPaillaco.models import AsistenciaPDF

from django.http import FileResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def ver_pdff(request):
    # Verificar si el usuario tiene un perfil asociado
    perfil_usuario = getattr(request.user, 'perfilusuario', None)
    if not perfil_usuario:
        return render(request, 'ver_pdff.html', {
            'error': "No se ha encontrado un perfil de usuario asociado."
        })

    # Obtener los parámetros de mes y año desde la URL (GET)
    mes = request.GET.get('mes', '').strip().lower()  # Convertimos a minúsculas
    ano = request.GET.get('ano', '').strip()

    # Validar que los parámetros sean correctos
    if not mes or not ano.isdigit():
        return render(request, 'ver_pdff.html', {
            'error': "Debe proporcionar un mes y un año válidos."
        })

    ano = int(ano)  # Convertimos el año a entero

    # Buscar el PDF más reciente si hay más de uno
    asistencia_pdf = AsistenciaPDF.objects.filter(
        perfil_usuario=perfil_usuario,
        mes_asistencia=mes,
        ano_asistencia=ano
    ).order_by('-id').first()  # Obtiene el último PDF generado

    # Si no se encontró un PDF, mostrar mensaje de error
    if not asistencia_pdf:
        return render(request, 'ver_pdff.html', {
            'mes': mes,
            'ano': ano,
            'perfil_usuario': perfil_usuario,
            'error': "No se ha encontrado un PDF para este mes y año."
        })

    # Obtener la ruta del archivo PDF
    archivo_pdf = asistencia_pdf.archivo_pdf.path

    # Obtener el nombre del funcionario directamente desde el modelo Asistencia
    # Tomamos el nombre de la asistencia correspondiente al mes y año
    asistencia = Asistencia.objects.filter(
        rut=perfil_usuario.rut,
        mes=mes,
        ano=ano
    ).first()  # Asumimos que hay al menos una asistencia para este perfil

    if not asistencia:
        return render(request, 'ver_pdff.html', {
            'error': "No se encontró asistencia para este funcionario en el mes y año solicitados."
        })

    nombre_funcionario = asistencia.nombre
    nombre_funcionario = nombre_funcionario.upper()  # Convertir a mayúsculas

    # Formatear el mes
    mes_formateado = mes.capitalize()  # Convertir a formato de mes con primera letra mayúscula

    # Construir el nombre del archivo
    nombre_pdf = f"{nombre_funcionario}_{mes_formateado}_{ano}.pdf"

    # Devolver el archivo PDF como respuesta de descarga con el nuevo nombre
    response = FileResponse(open(archivo_pdf, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_pdf}"'

    return response











def ver_pdf(request, asistencia_id):
    asistencia = Asistencia.objects.get(id=asistencia_id)
    return render(request, 'ver_pdf.html', {'asistencia': asistencia})






















