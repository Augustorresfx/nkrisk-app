from django import forms
from .models import Vehiculo, Flota

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['flota', 'cod_infoauto', 'marca', 'modelo', 'tipo_vehiculo', 'patente', 'anio', 'okm', 'zona', 'fecha_operacion', 'fecha_vigencia', 'operacion', 'tipo_cobertura', 'suma_asegurada', 'prima']
        widgets = {
            'flota': forms.Select(attrs={
                'class': 'form-select'
            }),
        }