from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class Vencimiento(models.Model):
    asegurador = models.CharField(null=True, blank=True, max_length=100)
    riesgo = models.CharField(null=True, blank=True, max_length=100)
    productor = models.CharField(null=True, blank=True, max_length=100)
    cliente = models.CharField(null=True, blank=True, max_length=100)
    poliza = models.CharField(max_length=100, null=True, blank=True)
    endoso = models.CharField(max_length=100, null=True, blank=True)
    cuota = models.IntegerField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    moneda = models.CharField(max_length=100, null=True, blank=True)
    importe = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    saldo = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    forma_pago = models.CharField(null=True, blank=True, max_length=100)
    factura = models.CharField(null=True, blank=True, max_length=100)
    
    class Meta: 
        ordering = ('poliza',)
        verbose_name_plural = 'Cobranzas'
        
        def __str__(self):
            return self.poliza
        
class Flota(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    cuit = models.CharField(max_length=100, blank=True, null=True)
    nacionalidad = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    localidad = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=254)
    
    class Meta: 
        ordering = ('created',)
        verbose_name_plural = 'Flotas'
        
        def __str__(self):
            return f"{self.nombre_cliente} - Flota ID: {self.id}"
    
    
class Vehiculo(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    flota = models.ForeignKey(Flota, on_delete=models.CASCADE)
    cod_infoauto = models.IntegerField(null=True, blank=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    tipo_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    patente = models.CharField(max_length=100, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    okm = models.CharField(max_length=100, blank=True, null=True)
    zona = models.CharField(max_length=100, blank=True, null=True)
    fecha_operacion = models.DateTimeField(null=True, blank=True)
    fecha_vigencia = models.DateTimeField(null=True, blank=True)
    operacion = models.CharField(max_length=100, blank=True, null=True)
    tipo_cobertura = models.CharField(max_length=100, blank=True, null=True)
    suma_asegurada = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    prima = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    
class TarifaFlota(models.Model):
    titulo = models.CharField(max_length=100, blank=True, null=True)
    zona = models.CharField(max_length=100, blank=True, null=True)
    tipo_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    antiguedad = models.CharField(max_length=100, blank=True, null=True)
    tipo_cobertura = models.CharField(max_length=100, blank=True, null=True)
    tasa = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    prima_rc_anual = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)