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
    "WA4": "AUTO",
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

def convert_tipo_cobertura(tipo_cobertura):
    tipo_cobertura_a_formatear = {
        "TODO AUTO FCIA. IMP. $112.500.-": "COB TODO AUTO",
        "POLIZA CLASICA": "COB CLASICA",
        "TODO RIESGO CON FRANQUICIA $75.000": "COB TODO AUTO",
        "A - RESPONSABILIDAD CIVIL": "",
    }
    return tipo_cobertura_a_formatear.get(tipo_cobertura, "")
            
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
        flota = data['flota'],
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
    
    # FUNCION ANTERIOR PARA CALCULAR PRIMA Y PREMIO EN EXCEL DE FLOTA 
    """ if "calcular_excel" in request.POST:
            created = datetime.now()
            nombre_movimiento = request.POST.get('nombre_movimiento')
            tipo_movimiento = request.POST.get('tipo_movimiento')
            # Mapeo de tipos a cadenas
            tipo_mapping = {
                "1": 'Combinado',
                "2": 'Alta',
                "3": 'Baja',
            }
            # Obtener la instancia de la Flota por su id
            flota = Flota.objects.get(pk=flota_id)

            # Acceder al cliente relacionado
            cliente = flota.cliente
            # Obtener el valor correspondiente o 'No especificado' si el tipo no está en el diccionario
            tipo_string = tipo_mapping.get(tipo_movimiento, 'No especificado')
            
            nuevo_movimiento = Movimiento(
                created = created,
                nombre_movimiento = nombre_movimiento,
                tipo_movimiento = tipo_string,
                flota = flota,
                cliente = cliente,
                
            )
            nuevo_movimiento.save()

            file1 = request.FILES.get('file1')
            workbook = openpyxl.load_workbook(file1)
            sheet = workbook.active
            for row_number, (marca, modelo, tipo_vehiculo, patente, anio, okm, importado, zona, fecha_operacion, fecha_vigencia_str, operacion, cobertura, suma_asegurada, _, _, _, _) in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                row_values = sheet.cell(row=row_number, column=1).value
                if row_values is None:
                    # Salir del bucle si la fila está vacía
                    break
                anio_vehiculo = anio
                anio_actual = datetime.now().year
                
                
                antiguedad_vehiculo = anio_actual - anio_vehiculo
                fecha_vigencia = fecha_vigencia_str
                anio_a_calcular = anio_actual if fecha_vigencia.year == anio_actual else anio_actual + 1
                print(anio_a_calcular)
                # Mapeo de antigüedad a categoría
                if antiguedad_vehiculo > 10:
                    antiguedad_categoria = "MÁS DE 10"
                elif 6 <= antiguedad_vehiculo <= 10:
                    antiguedad_categoria = "6 A 10"
                else:
                    antiguedad_categoria = "5"
                
                try:    
                    tarifa = TarifaFlota.objects.get(
                        tipo_vehiculo=tipo_vehiculo,
                        antiguedad=antiguedad_categoria,
                        zona__icontains=zona,
                        tipo_cobertura__contains=cobertura,
                    )
                except: 
                    error_message = f"No se encontró tarifa para {tipo_vehiculo}, {antiguedad_categoria}, {zona}, {cobertura}"
                    print(error_message)
                    lista_errores.append(error_message)  # Agregar el mensaje a una lista de errores
                tasa = tarifa.tasa
                prima_rc_anual = tarifa.prima_rc_anual
                print(tasa)
                print(tasa/1000)
                print("Rc:", prima_rc_anual)
                # Impuestos
                derecho_emision = 2400
                recargo_administrativo = Decimal('10.5')
                cien = Decimal('100')
                recargo_financiero = Decimal('5.68')
                cobertura_nacional = 75000
                cobertura_importado = 112500
                imp_y_sellados = Decimal('5.2')
                iva_21 = Decimal('21')
                iva_rg_3337 = Decimal('3')
                
                prima_tecnica_anual = (suma_asegurada * (tasa / 1000)) + prima_rc_anual 
                print(prima_tecnica_anual)
                prima_por_recargo_administrativo = (prima_tecnica_anual * recargo_administrativo) / cien
                prima_pza_anual = prima_tecnica_anual + prima_por_recargo_administrativo + derecho_emision
                print("Prima 10,5%: ",prima_por_recargo_administrativo)

                # Determinar si el año siguiente es bisiesto
                dias_totales = 366 if calendar.isleap(anio_a_calcular) else 365

                # Calcular los días de vigencia
                dias_vigencia = (fecha_vigencia - fecha_operacion).days
                print("Dias vigencia: ",dias_vigencia)
                print("Dias totales: ", dias_totales)
                print("Dias vigencia / dias totales:",dias_vigencia/dias_totales)
            
                prima_tecnica_vigente = prima_tecnica_anual * dias_vigencia / dias_totales
                prima_pza_vigente = prima_pza_anual * dias_vigencia / dias_totales

                

                # Determinar la cobertura según si la unidad es importada o no
                cobertura = cobertura_importado if importado == "SI" else cobertura_nacional

                premio_anual = prima_pza_anual + cobertura + ((prima_pza_anual * recargo_financiero) / cien)
                premio_vigente_sin_iva = prima_pza_vigente + ((prima_pza_vigente * recargo_financiero) / cien)
                premio_vigente_con_iva = premio_vigente_sin_iva + ((premio_vigente_sin_iva * imp_y_sellados) / cien) + ((premio_vigente_sin_iva * iva_21) / cien) + ((premio_vigente_sin_iva * iva_rg_3337) / cien)
                
                print(premio_vigente_sin_iva)
                print(premio_vigente_sin_iva * 3 / 100)
                print(premio_vigente_sin_iva * iva_21 / cien)
                print(premio_vigente_sin_iva * imp_y_sellados / cien)
                
                # Redondear valores
                prima_tecnica_vigente = round(prima_tecnica_vigente, 2)
                prima_pza_vigente = round(prima_pza_vigente, 2)
                premio_vigente_sin_iva = round(premio_vigente_sin_iva, 2)
                premio_vigente_con_iva = round(premio_vigente_con_iva, 2)

                if operacion == "BAJA":
                    prima_tecnica_vigente = -prima_tecnica_vigente
                    prima_pza_vigente = -prima_pza_vigente
                    premio_vigente_sin_iva = -premio_vigente_sin_iva
                    premio_vigente_con_iva = -premio_vigente_con_iva

                
                # Actualizar los valores en las columnas existentes
                sheet.cell(row=row_number, column=sheet.max_column - 3, value=prima_tecnica_vigente)  # Actualizar la columna de Prima Anual
                sheet.cell(row=row_number, column=sheet.max_column - 2, value=prima_pza_vigente)  # Actualizar la columna de Prima Vigente
                sheet.cell(row=row_number, column=sheet.max_column - 1, value=premio_vigente_sin_iva)  # Actualizar la columna de Prremio Anual
                sheet.cell(row=row_number, column=sheet.max_column, value=premio_vigente_con_iva)  # Actualizar la columna de Premio Vigente
                        
                # Crear una nueva instancia de Vehiculo
                vehiculo = Vehiculo(
                    created = created,
                    movimiento = nuevo_movimiento,
                    marca = marca,
                    modelo=modelo,
                    tipo_vehiculo=tipo_vehiculo,
                    patente=patente,
                    anio=anio,
                    okm = okm,
                    importado = importado,
                    zona = zona,
                    fecha_operacion = fecha_operacion,
                    fecha_vigencia = fecha_vigencia,
                    operacion = operacion,
                    tipo_cobertura = cobertura,
                    suma_asegurada = suma_asegurada,
                    prima_tecnica = prima_tecnica_vigente,
                    prima_pza = prima_pza_vigente,
                    premio_sin_iva = premio_vigente_sin_iva,
                    premio_con_iva = premio_vigente_con_iva,
                    
                )
                vehiculo.save()
                # Guardar la hoja de cálculo actualizada
            output = BytesIO()
            workbook.save(output)
            output.seek(0)

            # Crear una respuesta HTTP con el archivo adjunto
            response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=resultados_actualizados.xlsx'

            return response """