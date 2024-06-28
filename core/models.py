from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from simple_history.models import HistoricalRecords

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
    nombre_localidad = models.CharField(null=True, blank=True, max_length=100, db_index=True)
    nombre_municipio = models.CharField(null=True, blank=True, max_length=100)
    nombre_provincia = models.CharField(null=True, blank=True, max_length=100, db_index=True)
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
    recargo_financiero = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    imp_y_sellados = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    iibb = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    iva = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    
    
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
        return str(self.numero_flota)

class Movimiento(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    numero_endoso = models.CharField(max_length=100, blank=True, null=True)
    motivo_endoso = models.CharField(max_length=140, blank=True, null=True)
    flota = models.ForeignKey(Flota, on_delete=models.CASCADE)
    numero_orden = models.CharField(max_length=100, blank=True, null=True)
    vigencia_desde = models.DateField(blank=True, null=True)
    vigencia_hasta = models.DateField(blank=True, null=True)
    fecha_alta_op = models.DateField(blank=True, null=True)
    prima_tec_total = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    prima_pza_total = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    premio_sin_iva_total = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    premio_con_iva_total = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    prima_pza_porcentaje_diferencia = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    premio_con_iva_porcentaje_diferencia = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    

class VehiculoFlota(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    cod = models.IntegerField(null=True, blank=True)
    flota = models.ForeignKey(Flota, on_delete=models.CASCADE)
    movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    tipo_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    usuario_item = models.CharField(max_length=255, blank=True, null=True)
    patente = models.CharField(max_length=100, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    okm = models.CharField(max_length=100, blank=True, null=True)
    motor = models.CharField(max_length=100, blank=True, null=True)
    chasis = models.CharField(max_length=100, blank=True, null=True)
    localidad = models.CharField(max_length=100, blank=True, null=True)
    zona = models.CharField(max_length=100, blank=True, null=True)
    vigencia_desde = models.DateField(null=True, blank=True)
    vigencia_hasta = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    uso_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    suma_asegurada = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    valor_actual = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    tipo_cobertura = models.CharField(max_length=100, blank=True, null=True)
    tasa = models.DecimalField(decimal_places=3, max_digits=100, null=True, blank=True)
    prima_rc = models.DecimalField(decimal_places=3, max_digits=100, null=True, blank=True)
    tiene_accesorios = models.CharField(max_length=100, blank=True, null=True)
    suma_asegurada_accesorios = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    observacion = models.CharField(max_length=100, blank=True, null=True)
    prima_tecnica = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    prima_pza = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    premio_sin_iva = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    premio_con_iva = models.DecimalField(decimal_places=2, max_digits=100, null=True, blank=True)
    history = HistoricalRecords()
    
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
    
class CoberturaInnominada(models.Model):
    id_nacional = models.CharField(max_length=100)
    nombre_cliente = models.CharField(max_length=100)
    fecha_primer_consulta = models.DateTimeField(null=True, blank=True)
    fecha_ultima_consulta = models.DateTimeField(null=True, blank=True)
    codigoAutorizacion = models.CharField(max_length=100)
    fecha_hasta = models.DateTimeField(null=True, blank=True)
    codigoAsegurado = models.CharField(max_length=100, null=True, blank=True)
    
class CoberturaNominada(models.Model):
    id_nacional = models.CharField(max_length=100)
    pais = models.CharField(max_length=25)
    ciudad = models.CharField(max_length=100)
    cliente = models.CharField(max_length=100)
    vigencia_desde = models.DateTimeField(null=True, blank=True)
    vigencia_hasta = models.DateTimeField(null=True, blank=True)
    moneda = models.CharField(max_length=5)
    monto_solicitado = models.IntegerField()
    monto_aprobado = models.IntegerField()
    estado = models.CharField(max_length=14)
    condicion_de_venta = models.TextField()
    linea_de_negocios = models.IntegerField(null=True, blank=True)
    plazo_en_dias = models.IntegerField()
    codigoAsegurado = models.CharField(max_length=100, null=True, blank=True)
    observaciones = models.TextField()