from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

def access_expiration():
    return timezone.now() + timezone.timedelta(hours=1)

def refresh_expiration():
    return timezone.now() + timezone.timedelta(hours=24)

class AccessToken(models.Model):
    token = models.CharField(max_length=500)
    expiracion = models.DateTimeField(default=access_expiration)
    
    class Meta:
        get_latest_by = 'expiracion'
    
class RefreshToken(models.Model):
    token = models.CharField(max_length=500)
    expiracion = models.DateTimeField(default=refresh_expiration)
    
    class Meta:
        get_latest_by = 'expiracion'
        
class Localidad(models.Model):
    nombre_localidad = models.CharField(null=True, blank=True, max_length=100)
    nombre_municipio = models.CharField(null=True, blank=True, max_length=100)
    nombre_provincia = models.CharField(null=True, blank=True, max_length=100)
    zona = models.CharField(null=True, blank=True, max_length=100)
    
class Vencimiento(models.Model):
    asegurado = models.CharField(null=True, blank=True, max_length=100)
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
    
class TarifaFlota(models.Model):
    titulo = models.CharField(max_length=100, blank=True, null=True)
    zona = models.CharField(max_length=100, blank=True, null=True)
    tipo_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    antiguedad = models.CharField(max_length=100, blank=True, null=True)
    tipo_cobertura = models.CharField(max_length=100, blank=True, null=True)
    tasa = models.DecimalField(decimal_places=3, max_digits=100, null=True, blank=True)
    prima_rc_anual = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    
class Cliente(models.Model):
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    cuit = models.CharField(max_length=100, blank=True, null=True)
    nacionalidad = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    localidad = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=254)
    
    class Meta: 
        ordering = ('id',)
        verbose_name_plural = 'Clientes'
        
        def __str__(self):
            return {self.nombre_cliente}
        
class Flota(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    numero_flota = models.IntegerField(null=True, blank=True)
    poliza = models.IntegerField(null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta: 
        ordering = ('created',)
        verbose_name_plural = 'Flotas'
        
        def __str__(self):
            return self.numero_flota

class Movimiento(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    nombre_movimiento = models.CharField(max_length=100, blank=True, null=True)
    tipo_movimiento = models.CharField(max_length=100, blank=True, null=True)
    flota = models.ForeignKey(Flota, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)    
    
class VehiculoFlota(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    cod = models.IntegerField(null=True, blank=True)
    movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE, null=True, blank=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    tipo_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    patente = models.CharField(max_length=100, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    okm = models.CharField(max_length=100, blank=True, null=True)
    zona = models.CharField(max_length=100, blank=True, null=True)
    fecha_operacion = models.DateField(null=True, blank=True)
    fecha_vigencia = models.DateField(null=True, blank=True)
    operacion = models.CharField(max_length=100, blank=True, null=True)
    tipo_cobertura = models.CharField(max_length=100, blank=True, null=True)
    suma_asegurada = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    prima_tecnica = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    prima_pza = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    premio_sin_iva = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    premio_con_iva = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    
    
class MarcaInfoAuto(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre}"
    
class VehiculoInfoAuto(models.Model):
    codigo = models.CharField(max_length=100, blank=True, null=True)
    marca = models.ForeignKey(MarcaInfoAuto, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    nacionalidad = models.CharField(max_length=100, blank=True, null=True)
    tipo_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    precio_okm = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.descripcion}"
    
class PrecioAnual(models.Model):
    vehiculo = models.ForeignKey(VehiculoInfoAuto, on_delete=models.CASCADE)
    anio = models.IntegerField()
    precio = models.DecimalField(max_digits=20, decimal_places=2)
    
    def __str__(self):
        return f"{self.precio}"
    
    