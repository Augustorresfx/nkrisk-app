from django import forms
from .models import Vehiculo, Flota

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['flota', 'cod_infoauto', 'marca', 'modelo', 'patente', 'anio', 'okm', 'valor', 'prima']
        widgets = {
            'flota': forms.Select(attrs={
                'class': 'form-select'
            }),
        }