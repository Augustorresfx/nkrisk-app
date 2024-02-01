from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from datetime import datetime
from django.core.paginator import Paginator
from io import BytesIO
from decimal import Decimal
from django.core.files.base import ContentFile
from django.templatetags.static import static
import os
import calendar
from django.conf import settings
from copy import deepcopy, copy
from django.contrib import messages
from django.http import HttpResponseRedirect
import requests
from datetime import timedelta
from django.utils import timezone
import csv
from itertools import islice
from django.http import JsonResponse
from django.db.models import OuterRef, Subquery
from io import TextIOWrapper
from django.db import transaction
from django.http import HttpResponseNotFound

# Importe de formularios

# Importe de modelos
from .models import Vencimiento, Localidad, Flota, VehiculoFlota, VehiculoInfoAuto, MarcaInfoAuto, PrecioAnual, Movimiento, TarifaFlota, Cliente, AccessToken, RefreshToken, Localidad

# Importe de librerias
import pandas as pd
import openpyxl
from openpyxl.styles import NamedStyle

import xlwings as xw
from unidecode import unidecode

# Importe de funciones
from .api_auth import ApiAuthentication, AuthenticationError
from .api_manager import ApiManager
from .utils import get_vehicle_type, convert_tipo_cobertura, convert_date, handle_aumento_suma_asegurada, handle_baja_items, handle_cambio_cobertura, handle_modificacion_datos, handle_renovacion_alta_items


def pagina_no_encontrada(request, exception):
    print("Error 404 ocurrido")
    return HttpResponseNotFound(render(request, '404.html'))

class HomeView(View):
    def get(self, request, *args, **kwargs):
        context = {
            
        }
        return redirect('login')

# Inicio
@method_decorator(login_required, name='dispatch')    
class InicioView(View):
    def get(self, request, *args, **kwargs):
        
        context = {
            
        }
        return render(request, 'dashboard.html', context)
    def post(self, request, *args, **kwargs):
        lista_errores = []
        context = {
            'errores': lista_errores
        }
        if 'descargar_excel' in request.POST:
            # Nombre del archivo que quieres descargar
            file_path = os.path.join(settings.STATICFILES_DIRS[0], 'excel', 'modelo_ejemplo.xlsx')


            # Abre el archivo y lee su contenido
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=modelo_ejemplo.xlsx'
                return response
        if 'importar_localidades' in request.POST:
            file1 = request.FILES.get('file1')

            # Envuelve el archivo en un TextIOWrapper para manejar la codificación
            csv_file_wrapper = TextIOWrapper(file1.file, encoding='utf-8')

            # Usa DictReader para obtener un diccionario por fila
            csv_reader = csv.DictReader(csv_file_wrapper)

            # Itera sobre las filas del CSV
            for row_number, row in enumerate(csv_reader, start=2):
                municipio = row.get('municipio_nombre', '')
                localidad = row.get('nombre', '')
                provincia = row.get('provincia_nombre', '')
                zona = row.get('zona_nombre', '')

                # Crea el objeto Localidad
                Localidad.objects.create(
                    nombre_localidad=localidad,
                    nombre_municipio=municipio,
                    nombre_provincia=provincia,
                    zona=zona
                )

        if "calcular_excel" in request.POST:
            file1 = request.FILES.get('file1')
            workbook = openpyxl.load_workbook(file1)
            sheet = workbook.active
            for row_number, (marca, modelo, tipo_vehiculo, patente, anio, okm, importado, zona, fecha_operacion, fecha_vigencia, operacion, cobertura, suma_asegurada, _, _, _, _) in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                row_values = sheet.cell(row=row_number, column=1).value
                if row_values is None:
                    # Salir del bucle si la fila está vacía
                    break
                anio_vehiculo = anio
                anio_actual = datetime.now().year
                antiguedad_vehiculo = anio_actual - anio_vehiculo
                
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

                prima_anual = (suma_asegurada * (tasa / 1000)) + prima_rc_anual

                # Calcular los días de vigencia
                dias_vigencia = (fecha_vigencia - fecha_operacion).days

                prima_vigente = prima_anual * dias_vigencia / 365
                

                derecho_emision = 2400
                recargo_financiero = Decimal('5.68')
                cobertura_nacional = 75000
                cobertura_importado = 112500

                # Determinar la cobertura según si la unidad es importada o no
                cobertura = cobertura_importado if importado == "SI" else cobertura_nacional

                premio_anual = prima_anual + cobertura + derecho_emision + ((prima_anual * recargo_financiero) / 100)
                premio_vigente = prima_vigente + cobertura + derecho_emision + ((prima_vigente * recargo_financiero) / 100)

                if operacion == "BAJA":
                    prima_anual = -prima_anual
                    prima_vigente = -prima_vigente
                    premio_anual = -premio_anual
                    premio_vigente = -premio_vigente

                # Redondear valores
                premio_anual_redondeado = round(premio_anual, 2)
                premio_vigente_redondeado = round(premio_vigente, 2)
                prima_vigente_redondeada = round(prima_vigente, 2)
                # Actualizar los valores en las columnas existentes
                sheet.cell(row=row_number, column=sheet.max_column - 3, value=prima_anual)  # Actualizar la columna de Prima Anual
                sheet.cell(row=row_number, column=sheet.max_column - 2, value=prima_vigente_redondeada)  # Actualizar la columna de Prima Vigente
                sheet.cell(row=row_number, column=sheet.max_column - 1, value=premio_anual_redondeado)  # Actualizar la columna de Prremio Anual
                sheet.cell(row=row_number, column=sheet.max_column, value=premio_vigente_redondeado)  # Actualizar la columna de Premio Vigente
                        
                
                # Guardar la hoja de cálculo actualizada
            output = BytesIO()
            workbook.save(output)
            output.seek(0)

            # Crear una respuesta HTTP con el archivo adjunto
            response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=resultados_actualizados.xlsx'

            return response
        return render(request, 'dashboard.html', context)

# Clientes
@method_decorator(login_required, name='dispatch')
class ClientesView(View):
    def get(self, request, *args, **kwargs):
        clientes = Cliente.objects.all()
        
        clientes_paginados = Paginator(clientes, 30)
        page_number = request.GET.get("page")
        filter_pages = clientes_paginados.get_page(page_number)

        context = {
            'clientes': clientes, 
            'pages': filter_pages,

        }
        return render(request, 'clientes/clientes.html', context)
    def post(self, request, *args, **kwargs):
        # Obtén los datos del formulario directamente desde request.POST
        
        nombre = request.POST.get('nombre')
        cuit = request.POST.get('cuit')
        nacionalidad = request.POST.get('nacionalidad')
        provincia = request.POST.get('provincia')
        localidad = request.POST.get('localidad')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        recargo_financiero = request.POST.get('recargo_financiero')
        sellado_impuestos = request.POST.get('sellado_impuestos')
        iva = request.POST.get('iva')
        

        # Crea una nueva instancia de Flota
        nuevo_cliente = Cliente(
            
            nombre_cliente=nombre,
            cuit=cuit,
            nacionalidad=nacionalidad,
            provincia=provincia,
            localidad=localidad,
            direccion=direccion,
            telefono=telefono,
            email=email,
            recargo_financiero=recargo_financiero,
            sellado_impuestos=sellado_impuestos,
            iva=iva,
            
        )
        try:
            # Intenta crear el nuevo elemento
            nuevo_cliente.save()
            messages.success(request, 'El elemento se creó exitosamente.')
        except Exception as e:
            # Si hay un error al crear el elemento, captura la excepción
            messages.error(request, f'Error: No se pudo crear el elemento. Detalles: {str(e)}')

        # Redirige, incluyendo los mensajes en el contexto
        return HttpResponseRedirect(request.path_info)
    
@method_decorator(login_required, name='dispatch')   
class DetalleClienteView(View):
    def get(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)
        # Formatear los decimales para poder mostrarlos
        recargo_financiero_formatted = "{:.3f}".format(cliente.recargo_financiero).replace(',', '.')
        sellado_impuestos_formatted = "{:.3f}".format(cliente.sellado_impuestos).replace(',', '.')
        iva_formatted = "{:.3f}".format(cliente.iva).replace(',', '.')
    
        context = {
            'cliente': cliente,
            'recargo_financiero_formatted': recargo_financiero_formatted,
            'sellado_impuestos_formatted': sellado_impuestos_formatted,
            'iva_formatted': iva_formatted,
        }
        return render(request, 'clientes/detalle_cliente.html', context)

    def post(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)
        # Obtén los datos del formulario directamente desde request.POST
        nombre = request.POST.get('nombre')
        cuit = request.POST.get('cuit')
        nacionalidad = request.POST.get('nacionalidad')
        provincia = request.POST.get('provincia')
        localidad = request.POST.get('localidad')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        
        # Actualiza los campos de la tarifa con los datos del formulario
        cliente.nombre_cliente = nombre
        cliente.cuit = cuit
        cliente.nacionalidad = nacionalidad
        cliente.provincia = provincia
        cliente.localidad = localidad
        cliente.direccion = direccion
        cliente.telefono = telefono
        cliente.email = email
        try:
            # Intenta guardar la actualización del elemento
            cliente.save()
            messages.success(request, 'El elemento se actualizó exitosamente.')
        except Exception as e:
            # Si hay un error al actualizar el elemento, captura la excepción
            messages.error(request, f'Error: No se pudo actualizar el elemento. Detalles: {str(e)}')
        return redirect('clientes')

@method_decorator(login_required, name='dispatch')   
class EliminarClienteView(View):
    def get(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)
        
        context = {
            'cliente': cliente,
        }
        return redirect('clientes')

    def post(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)

        try:
            # Intenta guardar la eliminacion del elemento
            cliente.delete()
            messages.success(request, 'El elemento se eliminó exitosamente.')
        except Exception as e:
            # Si hay un error al eliminar el elemento, captura la excepción
            messages.error(request, f'Error: No se pudo eliminar el elemento. Detalles: {str(e)}')
        
        
        return redirect('clientes')
# Movimientos

@method_decorator(login_required, name='dispatch')   
class EliminarMovimientoView(View):
    def post(self, request, flota_id, movimiento_id):
        
        movimiento = get_object_or_404(Movimiento, id=movimiento_id)
        try:
            # Intenta guardar la eliminación del elemento
            movimiento.delete()
            messages.success(request, 'El elemento se eliminó exitosamente.')
        except Exception as e:
            # Si hay un error al eliminar el elemento, captura la excepción
            messages.error(request, f'Error: No se pudo eliminar el elemento. Detalles: {str(e)}')
        
        return redirect('detalle_flota', flota_id=flota_id)

@method_decorator(login_required, name='dispatch')   
class ExportarMovimientoView(View):
    def post(self, request, flota_id, movimiento_id):
        # Obtener movimiento
        movimiento = get_object_or_404(Movimiento, id=movimiento_id)
        # Nombre del archivo modelo
        file_path = os.path.join(settings.STATICFILES_DIRS[0], 'excel', 'modelo_ejemplo.xlsx')
        
        # Cargar el archivo Excel modelo
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        # Obtener los vehículos del movimiento
        vehiculos = VehiculoFlota.objects.filter(movimiento_id=movimiento_id)
        # Crear una copia del archivo Excel
        duplicated_workbook = openpyxl.Workbook()
        duplicated_sheet = duplicated_workbook.active

        # Iterar sobre las celdas de la primera fila y copiar los estilos relevantes
        for row in sheet.iter_rows(min_row=1, max_row=1):
            for cell in row:
                # Crear una nueva celda en la hoja de cálculo duplicada
                nueva_celda = duplicated_sheet.cell(row=1, column=cell.column, value=cell.value)

                # Copiar los estilos relevantes
                nueva_celda.fill = copy(cell.fill)  # Copiar el estilo de fondo (relleno)
                nueva_celda.border = copy(cell.border)  # Copiar los bordes
        # Iterar sobre los vehículos y llenar el archivo Excel duplicado
        for index, vehiculo in enumerate(vehiculos, start=2):

            duplicated_row = [None] * sheet.max_column  # Crear una lista para la nueva fila duplicada

            duplicated_row[0] = vehiculo.marca
            duplicated_row[1] = vehiculo.modelo
            duplicated_row[2] = vehiculo.tipo_vehiculo
            duplicated_row[3] = vehiculo.patente
            duplicated_row[4] = vehiculo.anio
            duplicated_row[5] = vehiculo.okm
            duplicated_row[6] = vehiculo.zona
            duplicated_row[7] = vehiculo.fecha_operacion.strftime('%d/%m/%Y')
            duplicated_row[8] = vehiculo.fecha_vigencia.strftime('%d/%m/%Y')
            duplicated_row[9] = vehiculo.operacion
            duplicated_row[10] = vehiculo.tipo_cobertura
            duplicated_row[11] = vehiculo.suma_asegurada
            duplicated_row[12] = vehiculo.prima_tecnica
            duplicated_row[13] = vehiculo.prima_pza
            duplicated_row[14] = vehiculo.premio_sin_iva
            duplicated_row[15] = vehiculo.premio_con_iva

            # Agregar más celdas según las columnas en tu archivo Excel

            # Agregar la nueva fila duplicada al archivo Excel duplicado
            duplicated_sheet.append(duplicated_row)
        # Crear una respuesta HTTP con el archivo Excel duplicado adjunto
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={movimiento.nombre_movimiento}.xlsx'
        duplicated_workbook.save(response)
        workbook.close()

        return response
        
        return redirect('detalle_flota', flota_id=flota_id)
    

# Flotas
@method_decorator(login_required, name='dispatch')
class FlotasView(View):
    def get(self, request, *args, **kwargs):
         # Obtenerel mes seleccionado desde la URL
        selected_month = request.GET.get("month")
        
        # Obtener el primer día del mes seleccionado
        if selected_month:
            selected_month = int(selected_month)
            start_date = datetime(datetime.now().year, selected_month, 1)
            end_date = datetime(datetime.now().year, selected_month + 1, 1) if selected_month < 12 else datetime(datetime.now().year + 1, 1, 1)
            
            # Filtrar las cobranzas para el mes seleccionado
            flotas = Flota.objects.filter(created__gte=start_date, created__lt=end_date).order_by('-created')
        else:
            # Si no se selecciona un mes, muestra todas las cobranzas
            flotas = Flota.objects.all().order_by('-created')
        
        flotas_paginadas = Paginator(flotas, 30)
        page_number = request.GET.get("page")
        filter_pages = flotas_paginadas.get_page(page_number)
        clientes = Cliente.objects.all()
        context = {
            'clientes': clientes,
            'flotas': flotas, 
            'pages': filter_pages,

        }
        return render(request, 'flotas/flotas.html', context)
    def post(self, request, *args, **kwargs):
        # Obtener los datos del formulario directamente desde request.POST
        created = datetime.now()
        numero_flota = request.POST.get('numero')
        poliza = request.POST.get('poliza')
        cliente_id = request.POST.get('cliente')
        
        
        cliente = Cliente.objects.get(pk=cliente_id)
        # Crear una nueva instancia de Flota
        nueva_flota = Flota(
            created = created,
            numero_flota = numero_flota,
            poliza = poliza,
            cliente = cliente,
            
        )
        try:
            # Intenta crear el nuevo elemento
            nueva_flota.save()
            messages.success(request, 'El elemento se creó exitosamente.')
        except Exception as e:
            # Si hay un error al crear el elemento, captura la excepción
            messages.error(request, f'Error: No se pudo crear el elemento. Detalles: {str(e)}')
        
        return redirect('flotas')

@method_decorator(login_required, name='dispatch')   
class EliminarFlotaView(View):
    def get(self, request, flota_id):
        flota = get_object_or_404(Flota, id=flota_id)

        context = {
            'flota': flota,
        }
        return redirect('flotas')

    def post(self, request, flota_id):
        flota = get_object_or_404(Flota, id=flota_id)
        
        try:
            # Intenta guardar la eliminación del elemento
            flota.delete()
            messages.success(request, 'El elemento se eliminó exitosamente.')
        except Exception as e:
            # Si hay un error al eliminar el elemento, captura la excepción
            messages.error(request, f'Error: No se pudo eliminar el elemento. Detalles: {str(e)}')

        return redirect('flotas')

# Flotas
@method_decorator(login_required, name='dispatch')
class DetalleFlotaView(View):
    def get(self, request, flota_id, movimiento_id=None, *args, **kwargs):
        selected_month = request.GET.get("month")
        # Obtener la flota
        flota = Flota.objects.get(id=flota_id)

        # Obtener todos los movimientos vinculados a esa flota
        movimientos = Movimiento.objects.filter(flota=flota).order_by('fecha_alta_op')

        if movimiento_id:
            # Si hay un movimiento_id específico, obtener ese movimiento
            movimiento = Movimiento.objects.filter(id=movimiento_id).first()

            if movimiento:
                # Obtener todos los vehículos vinculados a ese movimiento a lo largo de su historial
                vehiculos = VehiculoFlota.history.filter(movimiento=movimiento)
            else:
                # Si el movimiento no existe, establecer vehículos como vacío
                vehiculos = VehiculoFlota.history.none()
        else:
            
            vehiculos = VehiculoFlota.objects.filter(flota=flota)
        prima_tecnica_total = 0
        prima_pza_total = 0
        premio_sin_iva_total = 0
        premio_con_iva_total = 0

        for vehiculo in vehiculos:
            prima_tecnica_total += vehiculo.prima_tecnica
            prima_pza_total += vehiculo.prima_pza
            premio_sin_iva_total += vehiculo.premio_sin_iva
            premio_con_iva_total += vehiculo.premio_con_iva
        print(prima_tecnica_total)
        print(prima_pza_total)
        print(premio_sin_iva_total)
        print(premio_con_iva_total)
        page_number = request.GET.get("page")
        vehiculos_paginados = Paginator(vehiculos, 30)
        filter_pages = vehiculos_paginados.get_page(page_number)

        context = {
            'flota': flota,
            'vehiculos': vehiculos,
            'movimientos': movimientos,
            'pages': filter_pages,
        }
        
        return render(request, 'flotas/detalle_flota.html', context)
    @transaction.atomic
    def post(self, request, flota_id, *args, **kwargs):
        lista_errores = []
        flota = Flota.objects.get(id=flota_id)
        cliente = flota.cliente
        if 'descargar_excel' in request.POST:
            
            # Nombre del archivo que quieres descargar
            file_path = os.path.join(settings.STATICFILES_DIRS[0], 'excel', 'modelo_ejemplo.xlsx')

            # Abre el archivo y lee su contenido
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=modelo_ejemplo.xlsx'
                return response
        
        if "calcular_excel" in request.POST:
            created = datetime.now()
            api_manager = ApiManager()
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
            
            # Variables para el seguimiento del número de orden actual
            numero_orden_actual = None
            nuevo_movimiento = None
             
            file1 = request.FILES.get('file1')
            workbook = openpyxl.load_workbook(file1)
            sheet = workbook.active
            fuente_datos = request.POST.get('fuente_datos')
            
            # Si la fuente de datos será info auto, autenticarse
            if fuente_datos == 'info_auto':
                access_token = api_manager.get_valid_access_token()

            for row_number, (nro_orden, cliente_excel, productor, aseguradora, riesgo, tipo_refacturacion, vinculante, poliza, endoso, motivo_endoso, fecha_operacion_str, fecha_vigencia_str, prima, premio, estado, vigencia_desde, vigencia_hasta, clau_ajuste, codia, marca, modelo, descripcion, usuario_item, patente, anio, okm, motor, chasis, localidad_vehiculo, uso_vehiculo, suma_aseg, valor_actual, tipo_cobertura, tasa_excel, prima_rc_excel, prima_total, accesorios, clau_ajuste_item, suma_aseg_acc, acreedor, usuario, observacion, fecha_alta_op_str) in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                row_values = sheet.cell(row=row_number, column=1).value
                if row_values is None:
                    # Salir del bucle si la fila está vacía
                    break
                
                
                fecha_operacion = convert_date(fecha_operacion_str)
                fecha_vigencia = convert_date(fecha_vigencia_str)
                fecha_alta_op = fecha_alta_op_str.strftime("%Y-%m-%d")

                # Verificar si el número de orden cambió (crea un movimiento por c/nro de orden)
                if nro_orden != numero_orden_actual:
                    # Guardar el movimiento anterior si existe
                    if nuevo_movimiento:
                        nuevo_movimiento.save()

                    nuevo_movimiento = Movimiento(
                        created=created,
                        numero_endoso=endoso,
                        motivo_endoso=motivo_endoso,
                        flota=flota,
                        numero_orden=nro_orden,
                        vigencia_desde=fecha_operacion,
                        vigencia_hasta=fecha_vigencia,
                        fecha_alta_op=fecha_alta_op
                    )
                    nuevo_movimiento.save()

                # Actualizar el número de orden actual
                numero_orden_actual = nro_orden
                
                anio_vehiculo = int(anio)
                anio_actual = datetime.now().year
                
                # Formateo del tipo de cobertura
                tipo_de_cobertura = convert_tipo_cobertura(tipo_cobertura)
                print("Tipo de cobertura: ", tipo_de_cobertura)
                
                # Usar el precio de vehiculo que este en el Excel
                if fuente_datos == "excel":
                    precio = Decimal(suma_aseg)
                    vehiculo = VehiculoInfoAuto.objects.get(codigo=codia)
                    tipo_vehiculo = get_vehicle_type(vehiculo.tipo_vehiculo)
                    # Si el motivo es AUMENTO DE SUMA ASEGURADA buscar el vehiculo
                    if motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
                        vehiculo_anterior = VehiculoFlota.objects.filter(cod=codia, patente=patente).first()
                        # Si la suma asegurada es distinta el precio será la diferencia entre sumas
                        if suma_aseg != vehiculo_anterior.suma_asegurada:
                            precio = Decimal(suma_aseg) - vehiculo_anterior.suma_asegurada
                        # Si la suma no es distinta, no hay diferencia, por lo tanto el precio será cero
                        else:
                            precio = 0
                # Usar los datos de vehiculo de info auto
                elif fuente_datos == 'info_auto':
                    precios_vehiculo = api_manager.get_vehicle_price(access_token, codia)
                    tipo_vehiculo = api_manager.get_vehicle_features(access_token, codia)
                    # Obtener el último elemento de la lista (correspondiente al último año)
                    ultimo_ano = precios_vehiculo[-1]
                    
                    # Obtener el valor 'price' del último año
                    precio = ultimo_ano['price']
                    precio = None
                    
                    for precio_anual in precios_vehiculo:
                        if precio_anual['year'] == anio_vehiculo:
                            precio = precio_anual['price']
                            break
                        
                    # Si no se encuentra el precio para el año asignar 0 como valor
                    if precio is None:
                        precio = 0
                # Usar los datos de vehiculos de la base de datos propia
                elif fuente_datos == 'base_datos':
                    vehiculo = VehiculoInfoAuto.objects.get(codigo=codia)
                    precios_vehiculo =  PrecioAnual.objects.filter(vehiculo=vehiculo)
                    precio_anio = precios_vehiculo.get(anio=anio_vehiculo)
                    precio = precio_anio.precio
                    # Si no se encuentra el precio para el año asignar 0 como valor
                    if precio is None:
                        precio = 0
                        
                    tipo_vehiculo = get_vehicle_type(vehiculo.tipo_vehiculo)
                            
                # Calcula la antiguedad del vehiculo
                antiguedad_vehiculo = anio_actual - anio_vehiculo
                
                # Usa el año actual para calcular, si el año de la fecha de vigencia es distinto usa ese
                anio_a_calcular = anio_actual if fecha_vigencia.year == anio_actual else fecha_vigencia.year
                
                # Mapeo de antigüedad a categoría
                if antiguedad_vehiculo > 10:
                    antiguedad_categoria = "MÁS DE 10"
                elif 6 <= antiguedad_vehiculo <= 10:
                    antiguedad_categoria = "6 A 10"
                else:
                    antiguedad_categoria = "5"
                
                print(motivo_endoso)
                # Buscar zona de riesgo mediante la localidad que este en el Excel
                localidades_encontradas = Localidad.objects.filter(nombre_localidad=localidad_vehiculo)
                if localidades_encontradas.exists():
                    localidad = localidades_encontradas.first()
                    print(f"Localidad encontrada: {localidad.nombre_localidad}")
                    
                    print(f"Zona encontrada: {localidad.zona}")
                else:
                    error_message = f"No se encontró zona para la localidad: {localidad_vehiculo}"
                    print(error_message)
                    lista_errores.append(error_message)
                    
                # Buscar la tarifa
                try:
                    tarifa = TarifaFlota.objects.get(
                        tipo_vehiculo=tipo_vehiculo,
                        antiguedad=antiguedad_categoria,
                        zona=localidad.zona,
                        tipo_cobertura=tipo_de_cobertura,
                    )
                except:
                    error_message = f"No se encontró tarifa para {tipo_vehiculo}, {antiguedad_categoria}, {localidad.zona}, {tipo_de_cobertura}"
                    print(error_message)
                    lista_errores.append(error_message)  # Agregar el mensaje a una lista de errores
                
                # Si hay tasa en el excel y no es cero usar esa
                if tasa_excel and tasa_excel != 0.00:
                    tasa = tasa_excel
                # Si no hay tasa en el excel usar la de la tarifa encontrada
                else:
                    tasa = tarifa.tasa
                
                # Si hay prima_rc en el excel y no es cero usar esa
                if prima_rc_excel and prima_rc_excel != 0.00:
                    prima_rc_anual = prima_rc_excel
                # Si no hay prima rc en el excel usar la de la tarifa encontrada
                else:
                    prima_rc_anual = tarifa.prima_rc_anual
                
                print(tasa)
                print(tasa/1000)
                print("Rc:", prima_rc_anual)
                
                # Impuestos
                recargo_financiero = cliente.recargo_financiero
                imp_y_sellados = cliente.sellado_impuestos
                iva = cliente.iva
                
                # Constantes
                CIEN = Decimal('100')
                MIL = Decimal('1000')
                COBERTURA_NACIONAL = 75000
                COBERTURA_IMPORTADO = 112500
                RECARGO_ADMINISTRATIVO = Decimal('10.5')
                IVA_RG_3337 = Decimal('3')
                DERECHO_EMISION = 2400
                
                if motivo_endoso == 'AUMENTO DE SUMA ASEGURADA' or motivo_endoso == ' AUMENTO DE SUMA ASEGURADA':
                    # Si el motivo es aumento de suma y es diferente a la anterior, usar la tasa anterior, la prima rc se cobra una única vez
                    if suma_aseg != vehiculo_anterior.suma_asegurada:
                        tasa = vehiculo_anterior.tasa
                        prima_rc_anual = 0
                    # Si el motivo es aumento de suma y no es diferente a la anterior, no calcular nada (prima y premio = 0)
                    else:
                        prima_rc_anual = 0
                        tasa = 0
                        DERECHO_EMISION = 0
                        COBERTURA_IMPORTADO = 0
                        COBERTURA_NACIONAL = 0
                # CASO TRAILERS, AUTOELEVADORES Y TRACTORES QUE NO TIENEN SUMA ASEGURADA
                if suma_aseg == 0:
                   precio = 0
                   tasa = 0
                   
                # Si el motivo es renovación o alta de items hay que tener en cuenta la suma aseg de los accesorios en el total                
                if accesorios == 'SI' and motivo_endoso == 'RENOVACIÓN' or motivo_endoso == 'ALTA DE ITEMS':
                    precio += suma_aseg_acc
                
                # Cambiar el tipo de datos a Decimal para evitar errores en los cálculos
                precio = Decimal(str(precio))
                tasa = Decimal(str(tasa))
                prima_rc_anual = Decimal(str(prima_rc_anual))
                print(type(precio), precio)
                print(type(tasa), tasa)
                print(type(prima_rc_anual), prima_rc_anual)
                
                print("Tasa divido mil: ", tasa/MIL)
                # Calcular prima tecnica y prima póliza anual
                prima_tecnica_anual = (precio) * (tasa / MIL) + prima_rc_anual 
                print(prima_tecnica_anual)
                prima_por_recargo_administrativo = (prima_tecnica_anual * RECARGO_ADMINISTRATIVO) / CIEN
                prima_pza_anual = prima_tecnica_anual + prima_por_recargo_administrativo + DERECHO_EMISION
                print("Prima 10,5%: ",prima_por_recargo_administrativo)

                # Determinar si el año siguiente es bisiesto
                dias_totales = 366 if calendar.isleap(anio_a_calcular) else 365

                # Calcular los días de vigencia
                dias_vigencia = (fecha_vigencia - fecha_operacion).days
                
                # Cambiar el tipo de datos a Decimal para evitar errores en los cálculos
                dias_vigencia = Decimal(str(dias_vigencia))
                dias_totales = Decimal(str(dias_totales))
                print(type(dias_vigencia), dias_vigencia)
                print(type(dias_totales), dias_totales)
                print("Dias vigencia / dias totales:",dias_vigencia/dias_totales)
                dias_calculado = dias_vigencia/dias_totales
                
                print(type(dias_calculado), dias_calculado)
                # Calcular prima tecnica y prima póliza por la vigencia
                prima_tecnica_vigente = prima_tecnica_anual * dias_vigencia / dias_totales
                prima_pza_vigente = prima_pza_anual * dias_vigencia / dias_totales
                print(patente)
                print(prima_tecnica_vigente)
                print(prima_pza_vigente)
                # Determinar la cobertura según si la unidad es importada o no
                cobertura = COBERTURA_IMPORTADO if tipo_cobertura == "TODO AUTO FCIA. IMP. $112.500.-" else COBERTURA_NACIONAL
                print(type(recargo_financiero), recargo_financiero)
                print(type(imp_y_sellados), imp_y_sellados)
                print(type(iva), iva)
                
                # Calcular premio sin iva y con iva
                premio_anual = prima_pza_anual + cobertura + ((prima_pza_anual * recargo_financiero) / CIEN)
                premio_vigente_sin_iva = prima_pza_vigente + ((prima_pza_vigente * recargo_financiero) / CIEN)
                premio_vigente_con_iva = premio_vigente_sin_iva + ((premio_vigente_sin_iva * imp_y_sellados) / CIEN) + ((premio_vigente_sin_iva * iva) / CIEN)
                
                print("Premio sin iva: ", premio_vigente_sin_iva)
                
                print("Premio con iva: ", premio_vigente_con_iva)

                
                # Redondear valores
                prima_tecnica_vigente = round(prima_tecnica_vigente, 2)
                prima_pza_vigente = round(prima_pza_vigente, 2)
                premio_vigente_sin_iva = round(premio_vigente_sin_iva, 2)
                premio_vigente_con_iva = round(premio_vigente_con_iva, 2)

                # Si el movimiento es una baja los valores serán negativos
                if tipo_string == "Baja":
                    prima_tecnica_vigente = -prima_tecnica_vigente
                    prima_pza_vigente = -prima_pza_vigente
                    premio_vigente_sin_iva = -premio_vigente_sin_iva
                    premio_vigente_con_iva = -premio_vigente_con_iva
                
                # Actualizar los valores en las columnas existentes
                """"
                sheet.cell(row=row_number, column=sheet.max_column - 3, value=prima_tecnica_vigente)  # Actualizar la columna de Prima Anual
                sheet.cell(row=row_number, column=sheet.max_column - 2, value=prima_pza_vigente)  # Actualizar la columna de Prima Vigente
                sheet.cell(row=row_number, column=sheet.max_column - 1, value=premio_vigente_sin_iva)  # Actualizar la columna de Prremio Anual
                sheet.cell(row=row_number, column=sheet.max_column, value=premio_vigente_con_iva)  # Actualizar la columna de Premio Vigente
                """    
                
                # Crear un diccionario para mapear los motivos de endoso a las funciones correspondientes
                motivo_endoso_handlers = {
                    'MODIFIC. DATOS DEL VEHICULO AÑO  MODELO': handle_modificacion_datos,
                    'MODIFICACION DE DATOS DEL ASEGURADO': handle_modificacion_datos,
                    'MODIFICACION DE ITEMS': handle_modificacion_datos,
                    'AUMENTO DE SUMA ASEGURADA': handle_aumento_suma_asegurada,
                    ' AUMENTO DE SUMA ASEGURADA': handle_aumento_suma_asegurada,
                    'CAMBIO DE COBERTURA': handle_cambio_cobertura,
                    'BAJA DE ITEMS': handle_baja_items,
                }
                # Verificar si el vehículo ya existe
                existing_vehicle = VehiculoFlota.objects.filter(cod=codia, patente=patente, localidad=localidad_vehiculo).first()

                # Si existe, obtener el handler correspondiente al motivo de endoso y ejecutarlo
                if existing_vehicle and motivo_endoso in motivo_endoso_handlers:
                    data = {
                        'marca': marca,
                        'modelo': modelo,
                        'descripcion': descripcion,
                        'patente': patente,
                        'anio': anio,
                        'okm': okm,
                        'localidad_vehiculo': localidad_vehiculo,
                        'localidad': localidad,
                        'precio': precio,
                        'usuario_item': usuario_item,
                        'valor_actual': valor_actual,
                        'tipo_de_cobertura': tipo_de_cobertura,
                        'estado': estado,
                        'uso_vehiculo': uso_vehiculo,
                        'accesorios': accesorios,
                        'suma_aseg_acc': suma_aseg_acc,
                        'suma_aseg': suma_aseg,
                        'prima_tecnica_vigente': prima_tecnica_vigente,
                        'prima_pza_vigente': prima_pza_vigente,
                        'premio_vigente_sin_iva': premio_vigente_sin_iva,
                        'premio_vigente_con_iva': premio_vigente_con_iva,
                        'tasa': tasa,
                        'prima_rc_anual': prima_rc_anual,
                        'observacion': observacion,
                        'created': created,
                        'codia': codia,
                        'nuevo_movimiento': nuevo_movimiento,
                        'tipo_vehiculo': vehiculo.tipo_vehiculo,
                        'motor': motor,
                        'chasis': chasis,
                        'fecha_operacion': fecha_operacion,
                        'fecha_vigencia': fecha_vigencia,
                    }
                    motivo_endoso_handlers[motivo_endoso](existing_vehicle, data, nuevo_movimiento)
                
                elif not existing_vehicle and motivo_endoso == 'RENOVACIÓN' or motivo_endoso == 'ALTA DE ITEMS':
                    # Si no existe, crear un nuevo vehículo
                    print(type(flota), flota)
                    handle_renovacion_alta_items({
                        'created': created,
                        'codia': codia,
                        'flota': flota,
                        'nuevo_movimiento': nuevo_movimiento,
                        'marca': marca,
                        'modelo': modelo,
                        'descripcion': descripcion,
                        'tipo_vehiculo': vehiculo.tipo_vehiculo,
                        'usuario_item': usuario_item,
                        'patente': patente,
                        'anio': anio,
                        'okm': okm,
                        'motor': motor,
                        'chasis': chasis,
                        'localidad_vehiculo': localidad_vehiculo,
                        'localidad': localidad,
                        'fecha_operacion': fecha_operacion,
                        'fecha_vigencia': fecha_vigencia,
                        'estado': estado,
                        'uso_vehiculo': uso_vehiculo,
                        'precio': precio,
                        'valor_actual': valor_actual,
                        'tipo_de_cobertura': tipo_de_cobertura,
                        'tasa': tasa,
                        'prima_rc_anual': prima_rc_anual,
                        'accesorios': accesorios,
                        'suma_aseg_acc': suma_aseg_acc,
                        'observacion': observacion,
                        'prima_tecnica_vigente': prima_tecnica_vigente,
                        'prima_pza_vigente': prima_pza_vigente,
                        'premio_vigente_sin_iva': premio_vigente_sin_iva,
                        'premio_vigente_con_iva': premio_vigente_con_iva,
                    }, nuevo_movimiento)

            # Guardar la hoja de cálculo actualizada
            output = BytesIO()
            workbook.save(output)
            output.seek(0)
            # Guardar el último movimiento después de salir del bucle
            if nuevo_movimiento:
                nuevo_movimiento.save()
            # Crear una respuesta HTTP con el archivo adjunto
            response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=resultados_actualizados.xlsx'
            workbook.close()
            
            return response
                
        flota = Flota.objects.get(id=flota_id)
        cod_infoauto = request.POST.get('cod_infoauto')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        patente = request.POST.get('patente')
        anio = request.POST.get('anio')
        okm = request.POST.get('okm')
        valor = request.POST.get('valor')

        if cod_infoauto and marca:
            nuevo_vehiculo = VehiculoFlota(
                flota_id=flota_id,
                cod_infoauto=cod_infoauto,
                marca=marca,
                modelo=modelo,
                patente=patente,
                anio=anio,
                okm=okm,
                valor=valor,
            )
            nuevo_vehiculo.save()
            return redirect('detalle_flota', flota_id=flota_id)
        else:
            # Maneja errores de validación o muestra un mensaje de error
            return HttpResponse('Error: Datos de vehículo incompletos')
    
    #def calcular_datos_con_access_token(self, access_token):
        
# Tarifas flotas
@method_decorator(login_required, name='dispatch')
class DeleteAllTarifasFlotasView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Intenta guardar la eliminación del elemento
            TarifaFlota.objects.all().delete()  # Elimina todos los registros de Tarifas
            messages.success(request, 'Los datos se eliminaron exitosamente.')
        except Exception as e:
            # Si hay un error al eliminar el elemento, captura la excepción
            messages.error(request, f'Error: No se pudo eliminar los datos. Detalles: {str(e)}')
        
        return redirect('tarifas_flotas')
    
@method_decorator(login_required, name='dispatch')
class TarifasFlotasView(View):
    def get(self, request, *args, **kwargs):

        tarifas = TarifaFlota.objects.all()
    
        tarifas_paginadas = Paginator(tarifas, 30)
        page_number = request.GET.get("page")
        filter_pages = tarifas_paginadas.get_page(page_number)

        context = {
            'tarifas': tarifas, 
            'pages': filter_pages,

        }
        return render(request, 'tarifas_flotas/tarifas_flotas.html', context)
    def post(self, request, *args, **kwargs):
        
        if "delete_data" in request.POST:
            TarifaFlota.objects.all().delete()
            return redirect('tarifas_flotas')
        if "importar_excel" in request.POST:
            file1 = request.FILES.get('file1')
            workbook = openpyxl.load_workbook(file1)
            sheet = workbook.active
            for row in sheet.iter_rows(min_row=2, values_only=True):
                titulo, zona, tipo_vehiculo, antiguedad, tipo_cobertura, tasa, prima_rc_anual = row
                # Convierte las comas a puntos en los campos de tasa y prima_rc_anual
                #tasa = tasa.replace(',', '.') if tasa is not None else None
                #prima_rc_anual = prima_rc_anual.replace(',', '.') if prima_rc_anual is not None else None
                TarifaFlota.objects.create(
                    titulo = titulo,
                    zona = zona,
                    tipo_vehiculo = tipo_vehiculo,
                    antiguedad = antiguedad,
                    tipo_cobertura = tipo_cobertura,
                    tasa = tasa,
                    prima_rc_anual = prima_rc_anual
                )
            
        # Obtén los datos del formulario directamente desde request.POST
        titulo = request.POST.get('titulo')
        zona = request.POST.get('zona')
        tipo_vehiculo = request.POST.get('tipo_vehiculo')
        antiguedad = request.POST.get('antiguedad')
        tipo_cobertura = request.POST.get('tipo_cobertura')
        tasa = request.POST.get('tasa')
        prima_rc_anual = request.POST.get('prima_rc_anual')

        


        if not prima_rc_anual or not tasa:
         
            return redirect('tarifas_flotas')  # Redirige al usuario nuevamente al formulario

        # Crea una nueva instancia de Flota y guárdala en la base de datos
        nueva_tarifa_flota = TarifaFlota(
            titulo = titulo,
            zona = zona,
            tipo_vehiculo = tipo_vehiculo,
            antiguedad = antiguedad,
            tipo_cobertura = tipo_cobertura,
            tasa = tasa,
            prima_rc_anual = prima_rc_anual
            # Agrega los otros campos del formulario aquí
        )
        nueva_tarifa_flota.save()

        # Redirige a la página de flotas o realiza alguna otra acción que desees
        return redirect('tarifas_flotas')

@method_decorator(login_required, name='dispatch')   
class DetalleTarifaFlotaView(View):
    def get(self, request, tarifa_id):
        tarifa = get_object_or_404(TarifaFlota, id=tarifa_id)
        # Formatear los decimales para poder mostrarlos
        tasa_formatted = "{:.3f}".format(tarifa.tasa).replace(',', '.')
        prima_formatted = "{:.3f}".format(tarifa.prima_rc_anual).replace(',', '.')
        context = {
            'tarifa': tarifa,
            'tasa_formatted': tasa_formatted,
            'prima_formatted': prima_formatted,
        }
        return render(request, 'tarifas_flotas/detalle_tarifa_flota.html', context)

    def post(self, request, tarifa_id):
        tarifa = get_object_or_404(TarifaFlota, id=tarifa_id)
        # Obtén los datos del formulario directamente desde request.POST
        titulo = request.POST.get('titulo')
        zona = request.POST.get('zona')
        tipo_vehiculo = request.POST.get('tipo_vehiculo')
        antiguedad = request.POST.get('antiguedad')
        tipo_cobertura = request.POST.get('tipo_cobertura')
        tasa = request.POST.get('tasa')
        prima_rc_anual = request.POST.get('prima_rc_anual')
        
        # Actualiza los campos de la tarifa con los datos del formulario
        tarifa.titulo = titulo
        tarifa.zona = zona
        tarifa.tipo_vehiculo = tipo_vehiculo
        tarifa.antiguedad = antiguedad
        tarifa.tipo_cobertura = tipo_cobertura
        tarifa.tasa = tasa
        tarifa.prima_rc_anual = prima_rc_anual
        try:
            # Intenta guardar la actualización del elemento
            tarifa.save()
            messages.success(request, 'El elemento se actualizó exitosamente.')
        except Exception as e:
            # Si hay un error al actualizar el elemento, captura la excepción
            messages.error(request, f'Error: No se pudo actualizar el elemento. Detalles: {str(e)}')
        return redirect('tarifas_flotas')

@method_decorator(login_required, name='dispatch')   
class EliminarTarifaFlotaView(View):
    def get(self, request, tarifa_id):
        tarifa = get_object_or_404(TarifaFlota, id=tarifa_id)
        # Muestra una página de confirmación para la eliminación
        context = {
            'tarifa': tarifa,
        }
        return redirect('tarifas_flotas')

    def post(self, request, tarifa_id):
        tarifa = get_object_or_404(TarifaFlota, id=tarifa_id)

        try:
            # Intenta guardar la eliminación del elemento
            tarifa.delete()
            messages.success(request, 'El elemento se eliminó exitosamente.')
        except Exception as e:
            # Si hay un error al eliminar el elemento, captura la excepción
            messages.error(request, f'Error: No se pudo eliminar el elemento. Detalles: {str(e)}')


        return redirect('tarifas_flotas')


# Cobranzas
@method_decorator(login_required, name='dispatch')
class CobranzasView(View):
    def get(self, request, *args, **kwargs):
         # Obtén el mes seleccionado desde la URL
        selected_month = request.GET.get("month")
        
        # Obtiene el primer día del mes seleccionado
        if selected_month:
            selected_month = int(selected_month)
            start_date = datetime(datetime.now().year, selected_month, 1)
            end_date = datetime(datetime.now().year, selected_month + 1, 1) if selected_month < 12 else datetime(datetime.now().year + 1, 1, 1)
            
            # Filtra las cobranzas para el mes seleccionado
            vencimientos = Vencimiento.objects.filter(fecha_vencimiento__gte=start_date, fecha_vencimiento__lt=end_date).order_by('-fecha_vencimiento')
        else:
            # Si no se selecciona un mes, muestra todas las cobranzas
            vencimientos = Vencimiento.objects.all().order_by('-fecha_vencimiento')
        
        cobranzas_paginadas = Paginator(vencimientos, 30)
        page_number = request.GET.get("page")
        filter_pages = cobranzas_paginadas.get_page(page_number)

        context = {
            'vencimientos': vencimientos,  # Pasar las cobranzas al contexto
            'pages': filter_pages,

        }
        return render(request, 'cobranzas/cobranzas.html', context)
    
    
    def post(self, request, *args, **kwargs):
        if "delete_data" in request.POST:
            Vencimiento.objects.all().delete()  # Elimina todos los registros de Cobranza
            return redirect('cobranzas')
        
        
        selected_month = int(request.POST.get('month'))
        selected_year = int(request.POST.get('year'))
        file1 = request.FILES.get('file1')
        workbook = openpyxl.load_workbook(file1)
        sheet = workbook.active

        data = []  # Lista para almacenar las filas
        for row in sheet.iter_rows(min_row=4, values_only=True):
            asegurado, riesgo, productor, cliente, poliza, endoso, cuota, fecha_vencimiento, moneda, importe, saldo, forma_pago, factura = row
            # Si hay fecha cambia el formato al necesario por Django
            if fecha_vencimiento is not None:
                fecha_vencimiento = fecha_vencimiento.replace("/", "-")
                fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%d-%m-%Y")

                # Verifica si la fecha de vencimiento está en el mes y año seleccionados por el usuario
                if fecha_vencimiento.month == selected_month and fecha_vencimiento.year == selected_year:
                    data.append(row)  # Agrega la fila a la lista

                    # Procesa las filas de 100 en 100
                    if len(data) == 5:
                        self.process_data(data, selected_month, selected_year)
                        data = []  # Reinicia la lista para el siguiente lote

        # Procesa cualquier lote restante (menos de 100 filas)
        if data:
            self.process_data(data, selected_month, selected_year)
        
        context = {
            
        } 

        return redirect('cobranzas')
    
    def process_data(self, data, selected_month, selected_year):
        for row in data:
            asegurado, riesgo, productor, cliente, poliza, endoso, cuota, fecha_vencimiento, moneda, importe, saldo, forma_pago, factura = row
            # Si hay fecha de vencimiento cambia el formato al necesario por Django
            if fecha_vencimiento is not None:
                fecha_vencimiento = fecha_vencimiento.replace("/", "-")
                
                fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%d-%m-%Y")
                
                if fecha_vencimiento.month == selected_month and fecha_vencimiento.year == selected_year:
                    Vencimiento.objects.create(
                        asegurado=asegurado,
                        riesgo=riesgo,
                        productor=productor,
                        cliente=cliente,
                        poliza=poliza,
                        endoso=endoso,
                        cuota=cuota,
                        fecha_vencimiento=fecha_vencimiento,
                        moneda=moneda,
                        importe=importe,
                        saldo=saldo,
                        forma_pago=forma_pago,
                        factura=factura
                    )

# Vencimientos
@method_decorator(login_required, name='dispatch')
class VencimientosView(View):
    def get(self, request, *args, **kwargs):
         # Obtén el mes seleccionado desde la URL
        selected_month = request.GET.get("month")
        
        # Obtiene el primer día del mes seleccionado
        if selected_month:
            selected_month = int(selected_month)
            start_date = datetime(datetime.now().year, selected_month, 1)
            end_date = datetime(datetime.now().year, selected_month + 1, 1) if selected_month < 12 else datetime(datetime.now().year + 1, 1, 1)
            
            # Filtra las cobranzas para el mes seleccionado
            vencimientos = Vencimiento.objects.filter(fecha_vencimiento__gte=start_date, fecha_vencimiento__lt=end_date).order_by('-fecha_vencimiento')
        else:
            # Si no se selecciona un mes, muestra todas las cobranzas
            vencimientos = Vencimiento.objects.all().order_by('-fecha_vencimiento')
        
        cobranzas_paginadas = Paginator(vencimientos, 30)
        page_number = request.GET.get("page")
        filter_pages = cobranzas_paginadas.get_page(page_number)

        context = {
            'vencimientos': vencimientos,  # Pasar las cobranzas al contexto
            'pages': filter_pages,

        }
        return render(request, 'vencimientos/vencimientos.html', context)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if "delete_data" in request.POST:
            Vencimiento.objects.all().delete()  # Elimina todos los registros de Cobranza
            return redirect('vencimientos')
        
        
        selected_month = int(request.POST.get('month'))
        selected_year = int(request.POST.get('year'))
        file1 = request.FILES.get('file1')
        workbook = openpyxl.load_workbook(file1)
        sheet = workbook.active

        data = []  # Lista para almacenar las filas
        for row in sheet.iter_rows(min_row=4, values_only=True):
            asegurado, riesgo, productor, cliente, poliza, endoso, cuota, fecha_vencimiento, moneda, importe, saldo, forma_pago, factura = row
            # Si hay fecha cambia el formato al necesario por Django
            if fecha_vencimiento is not None:
                fecha_vencimiento = fecha_vencimiento.replace("/", "-")
                fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%d-%m-%Y")

                # Verifica si la fecha de vencimiento está en el mes y año seleccionados por el usuario
                if fecha_vencimiento.month == selected_month and fecha_vencimiento.year == selected_year:
                    data.append(row)  # Agrega la fila a la lista

                    # Procesa las filas de 100 en 100
                    if len(data) == 5:
                        self.process_data(data, selected_month, selected_year)
                        data = []  # Reinicia la lista para el siguiente lote

        # Procesa cualquier lote restante (menos de 100 filas)
        if data:
            self.process_data(data, selected_month, selected_year)
        
        context = {
            
        } 

        return redirect('vencimientos')
    
    def process_data(self, data, selected_month, selected_year):
        for row in data:
            asegurado, riesgo, productor, cliente, poliza, endoso, cuota, fecha_vencimiento, moneda, importe, saldo, forma_pago, factura = row
            # Si hay fecha de vencimiento cambia el formato al necesario por Django
            if fecha_vencimiento is not None:
                fecha_vencimiento = fecha_vencimiento.replace("/", "-")
                
                fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%d-%m-%Y")
                
                if fecha_vencimiento.month == selected_month and fecha_vencimiento.year == selected_year:
                    Vencimiento.objects.create(
                        asegurado=asegurado,
                        riesgo=riesgo,
                        productor=productor,
                        cliente=cliente,
                        poliza=poliza,
                        endoso=endoso,
                        cuota=cuota,
                        fecha_vencimiento=fecha_vencimiento,
                        moneda=moneda,
                        importe=importe,
                        saldo=saldo,
                        forma_pago=forma_pago,
                        factura=factura
                    )
                    
# Localidades
@method_decorator(login_required, name='dispatch')   
class LocalidadesView(View):
    def get(self, request, *args, **kwargs):
        localidades = Localidad.objects.all()
        cobranzas_paginadas = Paginator(localidades, 30)
        page_number = request.GET.get("page")
        filter_pages = cobranzas_paginadas.get_page(page_number)

        context = {
            'localidades': localidades, 
            'pages': filter_pages,

        }
        return render(request, 'localidades/localidades.html', context)
    def post(self, request, *args, **kwargs):
        lista_errores = []
        context = {
            'errores': lista_errores
        }
        if 'delete_data' in request.POST:
            Localidad.objects.all().delete()
            return redirect('localidades')
        if 'normalizar_nombres' in request.POST:
            localidades = Localidad.objects.all()
            for localidad in localidades:
                # Cambiar nombre a mayúsculas y sin tilde
                nombre_normalizado = unidecode(localidad.nombre_localidad.upper())
    
                # Actualiza el nombre de la localidad en la base de datos
                localidad.nombre_localidad = nombre_normalizado
                localidad.save()
        if 'importar_excel' in request.POST:
            file1 = request.FILES.get('file1')

            # Envuelve el archivo en un TextIOWrapper para manejar la codificación
            csv_file_wrapper = TextIOWrapper(file1.file, encoding='utf-8')

            # Usa DictReader para obtener un diccionario por fila
            csv_reader = csv.DictReader(csv_file_wrapper)

            # Itera sobre las filas del CSV
            for row_number, row in enumerate(csv_reader, start=2):
                municipio = row.get('municipio_nombre', '')
                localidad = row.get('nombre', '')
                provincia = row.get('provincia_nombre', '')
                zona = row.get('zona_nombre', '')

                # Crea el objeto Localidad
                Localidad.objects.create(
                    nombre_localidad=localidad,
                    nombre_municipio=municipio,
                    nombre_provincia=provincia,
                    zona=zona
                )
        return redirect('localidades')

# Buscar vehículo 

@login_required
def autocomplete_marcas(request):
    term = request.GET.get('term', '')
    marcas = MarcaInfoAuto.objects.filter(nombre__icontains=term).values('id', 'nombre')
    return JsonResponse(list(marcas), safe=False)

@login_required
def obtener_vehiculos_por_marca(request, marca_id):
    # Lógica para obtener vehículos por marca (ajusta esto según tus modelos)
    vehiculos = VehiculoInfoAuto.objects.filter(marca__id=marca_id).values('id', 'descripcion')

    # Devuelve la lista de vehículos en formato JSON
    return JsonResponse(list(vehiculos), safe=False)

@login_required
def obtener_datos_vehiculo(request, vehiculo_id):
        
        try:
            vehiculo = VehiculoInfoAuto.objects.get(pk=vehiculo_id)
            precios = PrecioAnual.objects.filter(vehiculo=vehiculo)
            # Obtener precios del vehículo
            precios = PrecioAnual.objects.filter(vehiculo=vehiculo).order_by('-anio')

            # Crear una lista de años y precios para enviar en la respuesta JSON
            anios_precios = [{'anio': precio.anio, 'precio': precio.precio} for precio in precios]
            
            data = {
                'codigo': vehiculo.codigo,
                'marca': vehiculo.marca.nombre,
                'descripcion': vehiculo.descripcion,
                'nacionalidad': vehiculo.nacionalidad,
                'precios': anios_precios,
                
                # ... otros campos que quieras incluir ...
            }
            if vehiculo.precio_okm:
                data['okm'] = vehiculo.precio_okm
            
            return JsonResponse(data)
        except VehiculoInfoAuto.DoesNotExist:
            return JsonResponse({'error': 'Vehículo no encontrado'}, status=404)

@method_decorator(login_required, name='dispatch')   
class BuscarVehiculoView(View):
    def get(self, request, *args, **kwargs):
        marcas = MarcaInfoAuto.objects.order_by('nombre')
        
        context = {
            'marcas': marcas,
        }
        return render(request, 'info_auto/buscar_vehiculo.html', context)

# Vehículos info auto
@method_decorator(login_required, name='dispatch')   
class VehiculosInfoAutoView(View):
    def get(self, request, *args, **kwargs):
        vehiculos = VehiculoInfoAuto.objects.order_by('marca__nombre')
        vehiculos_paginados = Paginator(vehiculos, 30)
        page_number = request.GET.get("page")
        filter_pages = vehiculos_paginados.get_page(page_number)

        context = {
            'vehiculos': vehiculos,
            'pages': filter_pages,

        }
        return render(request, 'info_auto/vehiculos_info_auto.html', context)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        lista_errores = []
        context = {
            'errores': lista_errores
        }
        if 'delete_data' in request.POST:
            VehiculoInfoAuto.objects.all().delete()
            return redirect('vehiculos')
        if 'importar_excel' in request.POST:

            file1 = request.FILES.get('file1')
            archivo_csv_texto = TextIOWrapper(file1, encoding='utf-8')
            datos_csv = csv.reader(islice(archivo_csv_texto, 3, None))

            # Itera sobre las filas del CSV
            for fila in datos_csv:
                
                cod =fila[0]
                marca =fila[1]
                descripcion =fila[2]
                nacionalidad =fila[3]
                tipo = fila[4]
                okm =fila[5]
                # Si la marca ya fue creada lo guardo en marca
                marca, created = MarcaInfoAuto.objects.get_or_create(nombre=marca)
                print(cod)
                print(marca)
                print(descripcion)
                print(tipo)
                print(okm)
                # Crear el objeto VehiculoInfoauto
                vehiculo = VehiculoInfoAuto.objects.create(
                    codigo=cod,
                    marca=marca,
                    descripcion=descripcion,
                    nacionalidad=nacionalidad,
                    tipo_vehiculo=tipo,

                )
                if okm != '':
                    okm_decimal = Decimal(okm.replace(',', '.'))  # Reemplaza ',' con '.' para manejar decimales
                    print("0km decimal: ", okm_decimal)
                    vehiculo.precio_okm = okm_decimal
                    vehiculo.save()
                # Iterar a través de los años y asignar precios si hay información
               
               
                for i, year in enumerate(range(2024, 2003, -1)):
                    precio_str = fila[i + 6] if i + 6 < len(fila) else None
                    if precio_str is not None and precio_str != '':
                        precio_decimal = Decimal(precio_str.replace(',', '.'))  # Reemplaza ',' con '.' para manejar decimales
                        print("Precio: ", precio_decimal)
                        PrecioAnual.objects.create(vehiculo=vehiculo, anio=year, precio=precio_decimal)
                       
                
        return redirect('vehiculos')
# Autenticación
class SignOutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')

class SignInView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('inicio')
        return render(request, 'login.html', {
            'form': AuthenticationForm()
        })

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inicio')
        
        return render(request, 'login.html', {
            'form': form,
            'error': 'El nombre de usuario o la contraseña no existen',
        })
        
# 1687, max lines