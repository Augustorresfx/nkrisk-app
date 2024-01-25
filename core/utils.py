from datetime import datetime

from datetime import datetime

from .models import VehiculoFlota
from decimal import Decimal

def convert_date(fecha_str):
    try:
        # Intenta convertir la cadena a un objeto datetime
        fecha_nueva = datetime.strptime(fecha_str, "%d/%m/%Y")
        return fecha_nueva
    except ValueError:
        # Si hay un error en la conversión, imprime un mensaje y retorna None
        print(f"Error en la conversión de fecha: {fecha_str}")
        return None

def get_vehicle_type(tipo_vehiculo):
    tipo_vehiculo_a_categoria = {
    "SE": "AUTO",
    "SED": "AUTO",
    "CAB": "AUTO",
    "CUP": "AUTO",
    "PKA": "PICK UP CLASE A",
    "FUA": "PICK UP CLASE A",
    "WA4": "PICK UP 4X4",
    "WAG": "AUTO",
    "RUR": "AUTO",
    "PKB": "PICK UP CLASE B",
    "PB4": "PICK UP CLASE B",
    "FUB": "PICK UP CLASE B",
    "JEE": "PICK UP 4X4",
    "MIV": "AUTO",
    "VAN": "AUTO",
    "MBU": "PICK UP CLASE B",
    "LIV": "PICK UP CLASE B",
    "PES": "PICK UP CLASE B",
    "SPE": "PICK UP CLASE B",
}
    return tipo_vehiculo_a_categoria.get(tipo_vehiculo, "Desconocido")
            
def handle_modificacion_datos(existing_vehicle, data, movimiento):
    existing_vehicle.marca = data['marca']
    existing_vehicle.modelo = data['modelo']
    existing_vehicle.descripcion = data['descripcion']
    existing_vehicle.patente = data['patente']
    existing_vehicle.anio = data['anio']
    existing_vehicle.okm = data['okm']
    existing_vehicle.localidad = data['localidad_vehiculo']
    existing_vehicle.zona = data['localidad'].zona
    existing_vehicle.suma_asegurada = data['precio']
    existing_vehicle.usuario_item = data['usuario_item']
    existing_vehicle.valor_actual = data['valor_actual']
    existing_vehicle.tipo_cobertura = data['tipo_de_cobertura']
    existing_vehicle.estado = data['estado']
    existing_vehicle.movimiento = movimiento
    existing_vehicle.uso_vehiculo = data['uso_vehiculo']
    existing_vehicle.tiene_accesorios = data['accesorios']
    if data['suma_aseg_acc'] != 0:
        existing_vehicle.suma_asegurada_accesorios = Decimal(data['suma_aseg_acc'])
    existing_vehicle.save()

def handle_aumento_suma_asegurada(existing_vehicle, data, movimiento):
    existing_vehicle.estado = data['estado']
    existing_vehicle.movimiento = movimiento
    existing_vehicle.tiene_accesorios = data['accesorios']
    existing_vehicle.suma_asegurada_accesorios = data['suma_aseg_acc']
    existing_vehicle.suma_asegurada = data['suma_aseg']
    existing_vehicle.prima_tecnica = existing_vehicle.prima_tecnica + data['prima_tecnica_vigente']
    existing_vehicle.prima_pza = existing_vehicle.prima_pza + data['prima_pza_vigente']
    existing_vehicle.premio_sin_iva = existing_vehicle.premio_sin_iva + data['premio_vigente_sin_iva']
    existing_vehicle.premio_con_iva = existing_vehicle.premio_con_iva + data['premio_vigente_con_iva']
    existing_vehicle.save()

def handle_cambio_cobertura(existing_vehicle, data, movimiento):
    existing_vehicle.estado = data['estado']
    existing_vehicle.movimiento = movimiento
    existing_vehicle.tipo_cobertura = data['tipo_de_cobertura']
    existing_vehicle.save()

def handle_baja_items(existing_vehicle, data, movimiento):
    existing_vehicle.estado = data['estado']
    existing_vehicle.movimiento = movimiento
    existing_vehicle.prima_tecnica = -data['prima_tecnica_vigente']
    existing_vehicle.prima_pza = -data['prima_pza_vigente']
    existing_vehicle.premio_sin_iva = -data['premio_vigente_sin_iva']
    existing_vehicle.premio_con_iva = -data['premio_vigente_con_iva']
    existing_vehicle.save()

def handle_renovacion_alta_items(data, movimiento):
    vehiculo = VehiculoFlota(
        created=data['created'],
        cod=data['codia'],

        marca=data['marca'],
        modelo=data['modelo'],
        movimiento=movimiento,
        descripcion=data['descripcion'],
        tipo_vehiculo=data['tipo_vehiculo'],
        usuario_item=data['usuario_item'],
        patente=data['patente'],
        anio=data['anio'],
        okm=data['okm'],
        motor=data['motor'],
        chasis=data['chasis'],
        localidad=data['localidad_vehiculo'],
        zona=data['localidad'].zona,
        vigencia_desde=data['fecha_operacion'],
        vigencia_hasta=data['fecha_vigencia'],
        estado=data['estado'],
        uso_vehiculo=data['uso_vehiculo'],
        suma_asegurada=data['precio'],
        valor_actual=data['valor_actual'],
        tipo_cobertura=data['tipo_de_cobertura'],
        tasa=data['tasa'],
        prima_rc=data['prima_rc_anual'],
        tiene_accesorios=data['accesorios'],
        suma_asegurada_accesorios=data['suma_aseg_acc'],
        observacion=data['observacion'],
        prima_tecnica=data['prima_tecnica_vigente'],
        prima_pza=data['prima_pza_vigente'],
        premio_sin_iva=data['premio_vigente_sin_iva'],
        premio_con_iva=data['premio_vigente_con_iva'],
    )
    vehiculo.save()