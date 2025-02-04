from django.contrib import admin
from django.urls import path
from App_SaludPaillaco.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='inicio'),
    path('registrarse/', registrarse, name='registrarse'),
    path('registro_exitoso/', registro_exitoso, name='registro_exitoso'),
    path('aceptacion_usuario/', aceptacion_usuario, name='aceptacion_usuario'),
    path('Panel_Administrador/', panel_administrador, name='panel_administrador'),
    path('cargar_excel/', cargar_excel, name='cargar_excel'),
    path('generar_pdf/', generar_pdf, name='generar_pdf'),
    path('panel_usuario_registrado/', panel_UsuarioRegistrado, name='usuario_registrado'),
    path('panel_usuario_no_registrado/', panel_UsuarioNoRegistrado, name='usuario_no_registrado'),
    path('ver_pdf/', ver_pdff, name='ver_pdf'),




    
]




