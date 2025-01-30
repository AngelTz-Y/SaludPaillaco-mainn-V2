from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Subir archivo Excel')
    
    
    
from django import forms

class AsistenciaForm(forms.Form):
    archivo_pdf = forms.FileField(label="Seleccionar archivo PDF", required=True)
    
    


