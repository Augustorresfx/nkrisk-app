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
from django.conf import settings
from copy import deepcopy, copy
from django.contrib import messages
from django.http import HttpResponseRedirect
# Importe de formularios

# Importe de modelos
from .models import Vencimiento, Flota, Vehiculo, Movimiento, TarifaFlota, Cliente

# Importe de librerias
import pandas as pd
import openpyxl
from openpyxl.styles import NamedStyle
import xlwings as xw
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
        

        # Crea una nueva instancia de Flota
        nuevo_cliente = Cliente(
            
            nombre_cliente=nombre,
            cuit=cuit,
            nacionalidad=nacionalidad,
            provincia=provincia,
            localidad=localidad,
            direccion=direccion,
            telefono=telefono,
            email=email
            
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
    
class DetalleClienteView(View):
    def get(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)

        context = {
            'cliente': cliente,

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
        vehiculos = Vehiculo.objects.filter(movimiento_id=movimiento_id)
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


            sheet.cell(row=index, column=1, value=vehiculo.marca)
            sheet.cell(row=index, column=2, value=vehiculo.modelo)
            sheet.cell(row=index, column=3, value=vehiculo.tipo_vehiculo)
            sheet.cell(row=index, column=4, value=vehiculo.patente)
            sheet.cell(row=index, column=5, value=vehiculo.anio)
            sheet.cell(row=index, column=6, value=vehiculo.okm)
            sheet.cell(row=index, column=7, value=vehiculo.importado)
            sheet.cell(row=index, column=8, value=vehiculo.zona)
            sheet.cell(row=index, column=9, value=vehiculo.fecha_operacion.strftime('%d/%m/%Y'))
            sheet.cell(row=index, column=10, value=vehiculo.fecha_vigencia.strftime('%d/%m/%Y'))
            sheet.cell(row=index, column=11, value=vehiculo.operacion)
            sheet.cell(row=index, column=12, value=vehiculo.tipo_cobertura)
            sheet.cell(row=index, column=13, value=vehiculo.suma_asegurada)
            sheet.cell(row=index, column=14, value=vehiculo.prima_anual)
            sheet.cell(row=index, column=15, value=vehiculo.prima_vigente)
            sheet.cell(row=index, column=16, value=vehiculo.premio_anual)
            sheet.cell(row=index, column=17, value=vehiculo.premio_vigente)
            
            # Agregar más celdas según las columnas en tu archivo Excel

        

        # Copiar los datos desde el archivo Excel original al duplicado
        for row in sheet.iter_rows(min_row=1, max_col=sheet.max_column, max_row=sheet.max_row):
            duplicated_sheet.append([cell.value for cell in row])

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
    def get(self, request, flota_id, *args, **kwargs):
        selected_month = request.GET.get("month")
        # Obtener la flota
        flota = Flota.objects.get(id=flota_id)
        vehiculos = []
        # Buscar el primer movimiento para esa flota
        primer_movimiento = Movimiento.objects.filter(flota=flota).order_by('created').first()

        if primer_movimiento:
            # Obtener los vehículos vinculados a ese movimiento
            vehiculos = Vehiculo.objects.filter(movimiento=primer_movimiento)
            # Obtener los movimientos vinculados a esa flota
            movimientos = Movimiento.objects.filter(flota=flota).order_by('-created')
            page_number = request.GET.get("page")
            
            vehiculos_paginados = Paginator(vehiculos, 30)
            filter_pages = vehiculos_paginados.get_page(page_number)
            context = {
                'flota': flota,
                'vehiculos': vehiculos,
                'movimientos': movimientos,
                'pages': filter_pages,
            }
        else:
            
            context = {
                'flota': flota,
                'vehiculos': None,
                'movimientos': None,
                
            }
        
        
        flota = Flota.objects.get(id=flota_id)
        
        return render(request, 'flotas/detalle_flota.html', context)
    def post(self, request, flota_id, *args, **kwargs):
        lista_errores = []
        
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
            print(tipo_movimiento)
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
                    prima_anual = prima_anual,
                    prima_vigente = prima_vigente_redondeada,
                    premio_anual = premio_anual_redondeado,
                    premio_vigente = premio_vigente_redondeado,
                    
                )
                vehiculo.save()
                # Guardar la hoja de cálculo actualizada
            output = BytesIO()
            workbook.save(output)
            output.seek(0)

            # Crear una respuesta HTTP con el archivo adjunto
            response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=resultados_actualizados.xlsx'

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
            nuevo_vehiculo = Vehiculo(
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

        # Agrega los otros campos del formulario aquí

        # Realiza la validación de los datos según tus necesidades
        if not prima_rc_anual or not tasa:
            # Maneja la validación aquí, por ejemplo, mostrando un mensaje de error
            # o redirigiendo al usuario nuevamente al formulario.
            # Puedes usar la biblioteca messages de Django para mostrar mensajes al usuario.
            # from django.contrib import messages
            # messages.error(request, 'Los campos requeridos no pueden estar en blanco.')
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

class DetalleTarifaFlotaView(View):
    def get(self, request, tarifa_id):
        tarifa = get_object_or_404(TarifaFlota, id=tarifa_id)
        # Crea un formulario de edición de tarifa personalizado aquí (por ejemplo, usando Django Forms)
        # Puedes pasar el formulario como contexto a tu plantilla de edición
        tasa_formatted = "{:.2f}".format(tarifa.tasa).replace(',', '.')
        prima_formatted = "{:.2f}".format(tarifa.prima_rc_anual).replace(',', '.')
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