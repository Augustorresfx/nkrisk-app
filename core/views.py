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

# Importe de formularios
from .forms import VehiculoForm

# Importe de modelos
from .models import Vencimiento, Flota, Vehiculo, TarifaFlota

# Importe de librerias
import pandas as pd
import openpyxl
import xlwings as xw
class HomeView(View):
    def get(self, request, *args, **kwargs):
        context = {
            
        }
        return redirect('login')

# Dashboard
@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request, *args, **kwargs):
        context = {
                
        }
        return render(request, 'index.html', context)
        

# Flotas
@method_decorator(login_required, name='dispatch')
class FlotasView(View):
    def get(self, request, *args, **kwargs):
         # Obtén el mes seleccionado desde la URL
        selected_month = request.GET.get("month")
        
        # Obtiene el primer día del mes seleccionado
        if selected_month:
            selected_month = int(selected_month)
            start_date = datetime(datetime.now().year, selected_month, 1)
            end_date = datetime(datetime.now().year, selected_month + 1, 1) if selected_month < 12 else datetime(datetime.now().year + 1, 1, 1)
            
            # Filtra las cobranzas para el mes seleccionado
            flotas = Flota.objects.filter(created__gte=start_date, created__lt=end_date).order_by('-created')
        else:
            # Si no se selecciona un mes, muestra todas las cobranzas
            flotas = Flota.objects.all().order_by('-created')
        
        flotas_paginadas = Paginator(flotas, 30)
        page_number = request.GET.get("page")
        filter_pages = flotas_paginadas.get_page(page_number)

        context = {
            'flotas': flotas, 
            'pages': filter_pages,

        }
        return render(request, 'flotas/flotas.html', context)
    def post(self, request, *args, **kwargs):
        # Obtén los datos del formulario directamente desde request.POST
        created = datetime.now()
        nombre = request.POST.get('nombre')
        cuit = request.POST.get('cuit')
        nacionalidad = request.POST.get('nacionalidad')
        provincia = request.POST.get('provincia')
        localidad = request.POST.get('localidad')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        # Agrega los otros campos del formulario aquí

        # Realiza la validación de los datos según tus necesidades
        if not nombre or not cuit:
            # Maneja la validación aquí, por ejemplo, mostrando un mensaje de error
            # o redirigiendo al usuario nuevamente al formulario.
            # Puedes usar la biblioteca messages de Django para mostrar mensajes al usuario.
            # from django.contrib import messages
            # messages.error(request, 'Los campos requeridos no pueden estar en blanco.')
            return redirect('flotas')  # Redirige al usuario nuevamente al formulario

        # Crea una nueva instancia de Flota y guárdala en la base de datos
        nueva_flota = Flota(
            created = created,
            nombre_cliente=nombre,
            cuit=cuit,
            nacionalidad=nacionalidad,
            provincia=provincia,
            localidad=localidad,
            direccion=direccion,
            telefono=telefono,
            email=email
            # Agrega los otros campos del formulario aquí
        )
        nueva_flota.save()

        # Redirige a la página de flotas o realiza alguna otra acción que desees
        return redirect('flotas')


# Flotas
@method_decorator(login_required, name='dispatch')
class DetalleFlotaView(View):
    def get(self, request, flota_id, *args, **kwargs):
        selected_month = request.GET.get("month")
        flota = Flota.objects.get(id=flota_id)
        # Obtiene el primer día del mes seleccionado
        if selected_month:
            selected_month = int(selected_month)
            start_date = datetime(datetime.now().year, selected_month, 1)
            end_date = datetime(datetime.now().year, selected_month + 1, 1) if selected_month < 12 else datetime(datetime.now().year + 1, 1, 1)
            
            # Filtra las cobranzas para el mes seleccionado
            vehiculos = Vehiculo.objects.filter(flota=flota).order_by('-created')
        else:
            # Si no se selecciona un mes, muestra todas las cobranzas
            vehiculos = Vehiculo.objects.filter(flota=flota).order_by('-created')
        
        vehiculos_paginados = Paginator(vehiculos, 30)
        page_number = request.GET.get("page")
        filter_pages = vehiculos_paginados.get_page(page_number)

        context = {
            'flota': flota,
            'vehiculos': vehiculos, 
            'pages': filter_pages,

        }
        flota = Flota.objects.get(id=flota_id)
        
        return render(request, 'flotas/detalle_flota.html', context)
    def post(self, request, flota_id, *args, **kwargs):
        if "calcular_excel" in request.POST:
            file1 = request.FILES.get('file1')
            workbook = openpyxl.load_workbook(file1)
            sheet = workbook.active
            for row_number, (marca, modelo, tipo_vehiculo, patente, anio, okm, importado, zona, fecha_operacion, fecha_vigencia, operacion, cobertura, suma_asegurada, _, _, _, _) in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):

                # marca, modelo, tipo_vehiculo, patente, anio, okm, zona, fecha_operacion, fecha_vigencia, operacion, cobertura, suma_asegurada, _, _ = row
                # Realizar cálculos según las fórmulas proporcionadas

                anio_vehiculo = anio
                anio_actual = datetime.now().year
                antiguedad_vehiculo = anio_actual - anio_vehiculo

                if antiguedad_vehiculo > 10:
                    tarifa = TarifaFlota.objects.get(
                        tipo_vehiculo = tipo_vehiculo,
                        antiguedad = "MÁS DE 10",
                        zona__contains = zona,
                        tipo_cobertura__contains = cobertura,
                    )
                elif antiguedad_vehiculo <= 10 and antiguedad_vehiculo >= 6:
                    tarifa = TarifaFlota.objects.get(
                        tipo_vehiculo = tipo_vehiculo,
                        antiguedad = "6 A 10",
                        zona__contains = zona,
                        tipo_cobertura__contains = cobertura,
                    )
                else:
                    tarifa = TarifaFlota.objects.get(
                        tipo_vehiculo = tipo_vehiculo,
                        antiguedad = "5",
                        zona__icontains = zona,
                        tipo_cobertura__contains = cobertura,
                    )


                tasa = tarifa.tasa  # Obtener la tasa desde la base de datos según la zona, tipo de vehículo, antigüedad y tipo de cobertura
                prima_rc_anual = tarifa.prima_rc_anual  # Obtener la prima_rc_anual desde la base de datos

                prima_anual = (suma_asegurada * (tasa / 1000)) + prima_rc_anual

                # Calcular los días de vigencia
                dias_vigencia = (fecha_vigencia - fecha_operacion).days

                prima_vigente = prima_anual * dias_vigencia / 365
                prima_vigente_redondeada = round(prima_vigente, 2)

                derecho_emision = 2400
                recargo_administrativo = Decimal('10.5')
                recargo_financiero = Decimal('5.68')
                cobertura_nacional = 75000
                cobertura_importado = 112500
                
                # Si operación es ALTA agregar el valor positivo, si es BAJA el valor pasa a ser negativo
                if(operacion == "ALTA"):
                    if(importado == "NO"):
                        premio_anual = prima_anual + cobertura_nacional + derecho_emision + ((prima_anual * recargo_financiero) / 100)
                        premio_vigente = prima_vigente + cobertura_nacional + derecho_emision + ((prima_vigente * recargo_financiero) / 100)
                        # Redondear valores
                        premio_anual_redondeado = round(premio_anual, 2)
                        premio_vigente_redondeado = round(premio_vigente, 2)
                        # Actualizar los valores en las columnas existentes
                        sheet.cell(row=row_number, column=sheet.max_column - 3, value=prima_anual)  # Actualizar la columna de Prima Anual
                        sheet.cell(row=row_number, column=sheet.max_column - 2, value=prima_vigente_redondeada)  # Actualizar la columna de Prima Vigente
                        sheet.cell(row=row_number, column=sheet.max_column - 1, value=premio_anual_redondeado)  # Actualizar la columna de Prremio Anual
                        sheet.cell(row=row_number, column=sheet.max_column, value=premio_vigente_redondeado)  # Actualizar la columna de Premio Vigente
                    else:
                        premio_anual = prima_anual + cobertura_importado + derecho_emision + ((prima_anual * recargo_financiero) / 100)
                        premio_vigente = prima_vigente + cobertura_importado + derecho_emision + ((prima_vigente * recargo_financiero) / 100)
                        # Redondear valores
                        premio_anual_redondeado = round(premio_anual, 2)
                        premio_vigente_redondeado = round(premio_vigente, 2)
                        # Actualizar los valores en las columnas existentes
                        sheet.cell(row=row_number, column=sheet.max_column - 3, value=prima_anual)  # Actualizar la columna de Prima Anual
                        sheet.cell(row=row_number, column=sheet.max_column - 2, value=prima_vigente_redondeada)  # Actualizar la columna de Prima Vigente
                        sheet.cell(row=row_number, column=sheet.max_column - 1, value=premio_anual_redondeado)  # Actualizar la columna de Prremio Anual
                        sheet.cell(row=row_number, column=sheet.max_column, value=premio_vigente_redondeado)  # Actualizar la columna de Premio Vigente
                           
                else:
                    if(importado == "NO"):
                        premio_anual = prima_anual + cobertura_nacional + derecho_emision + ((prima_anual * recargo_financiero) / 100)
                        premio_vigente = prima_vigente + cobertura_nacional + derecho_emision + ((prima_vigente * recargo_financiero) / 100)
                        # Redondear valores
                        premio_anual_redondeado = round(premio_anual, 2)
                        premio_vigente_redondeado = round(premio_vigente, 2)
                        # Actualizar los valores en las columnas existentes
                        sheet.cell(row=row_number, column=sheet.max_column - 3, value=-prima_anual)  # Actualizar la columna de Prima Anual
                        sheet.cell(row=row_number, column=sheet.max_column - 2, value=-prima_vigente_redondeada)  # Actualizar la columna de Prima Vigente
                        sheet.cell(row=row_number, column=sheet.max_column - 1, value=-premio_anual_redondeado)  # Actualizar la columna de Prremio Anual
                        sheet.cell(row=row_number, column=sheet.max_column, value=-premio_vigente_redondeado)  # Actualizar la columna de Premio Vigente
                    else:
                        premio_anual = prima_anual + cobertura_importado + derecho_emision + ((prima_anual * recargo_financiero) / 100)
                        premio_vigente = prima_vigente + cobertura_importado + derecho_emision + ((prima_vigente * recargo_financiero) / 100)
                        # Redondear valores
                        premio_anual_redondeado = round(premio_anual, 2)
                        premio_vigente_redondeado = round(premio_vigente, 2)
                        # Actualizar los valores en las columnas existentes
                        sheet.cell(row=row_number, column=sheet.max_column - 3, value=-prima_anual)  # Actualizar la columna de Prima Anual
                        sheet.cell(row=row_number, column=sheet.max_column - 2, value=-prima_vigente_redondeada)  # Actualizar la columna de Prima Vigente
                        sheet.cell(row=row_number, column=sheet.max_column - 1, value=-premio_anual_redondeado)  # Actualizar la columna de Prremio Anual
                        sheet.cell(row=row_number, column=sheet.max_column, value=-premio_vigente_redondeado)  # Actualizar la columna de Premio Vigente
                        
                
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
        
      
# Vehiculos
@method_decorator(login_required, name='dispatch')
class VehiculosView(View):
    def get(self, request, *args, **kwargs):
         # Obtén el mes seleccionado desde la URL
        selected_month = request.GET.get("month")
        form = VehiculoForm()
        # Obtiene el primer día del mes seleccionado
        if selected_month:
            selected_month = int(selected_month)
            start_date = datetime(datetime.now().year, selected_month, 1)
            end_date = datetime(datetime.now().year, selected_month + 1, 1) if selected_month < 12 else datetime(datetime.now().year + 1, 1, 1)
            
            # Filtra las cobranzas para el mes seleccionado
            vehiculos = Vehiculo.objects.filter(created__gte=start_date, created__lt=end_date).order_by('-created')
        else:
            # Si no se selecciona un mes, muestra todas las cobranzas
            vehiculos = Vehiculo.objects.all().order_by('-created')
        
        vehiculos_paginados = Paginator(vehiculos, 30)
        page_number = request.GET.get("page")
        filter_pages = vehiculos_paginados.get_page(page_number)

        context = {
            'form': form,
            'vehiculos': vehiculos,
            'pages': filter_pages,

        }
        return render(request, 'vehiculos/vehiculos.html', context)
    def post(self, request, *args, **kwargs):
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save()
            return redirect('vehiculos')
        else:
            form = VehiculoForm()
        return redirect('vehiculos')

# Tarifas flotas
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
            TarifaFlota.objects.all().delete()  # Elimina todos los registros de Tarifas
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
        tarifa.save()
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
        # Realiza la eliminación de la tarifa
        tarifa.delete()
        # Después de eliminar, redirige a la página de la lista de tarifas o a donde desees
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
            asegurador, riesgo, productor, cliente, poliza, endoso, cuota, fecha_vencimiento, moneda, importe, saldo, forma_pago, factura = row
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
            asegurador, riesgo, productor, cliente, poliza, endoso, cuota, fecha_vencimiento, moneda, importe, saldo, forma_pago, factura = row
            # Si hay fecha de vencimiento cambia el formato al necesario por Django
            if fecha_vencimiento is not None:
                fecha_vencimiento = fecha_vencimiento.replace("/", "-")
                
                fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%d-%m-%Y")
                
                if fecha_vencimiento.month == selected_month and fecha_vencimiento.year == selected_year:
                    Vencimiento.objects.create(
                        asegurador=asegurador,
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
            asegurador, riesgo, productor, cliente, poliza, endoso, cuota, fecha_vencimiento, moneda, importe, saldo, forma_pago, factura = row
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
            asegurador, riesgo, productor, cliente, poliza, endoso, cuota, fecha_vencimiento, moneda, importe, saldo, forma_pago, factura = row
            # Si hay fecha de vencimiento cambia el formato al necesario por Django
            if fecha_vencimiento is not None:
                fecha_vencimiento = fecha_vencimiento.replace("/", "-")
                
                fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%d-%m-%Y")
                
                if fecha_vencimiento.month == selected_month and fecha_vencimiento.year == selected_year:
                    Vencimiento.objects.create(
                        asegurador=asegurador,
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
        return redirect('home')

class SignInView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('vencimientos')
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
                return redirect('dashboard')
        
        return render(request, 'login.html', {
            'form': form,
            'error': 'El nombre de usuario o la contraseña no existen',
        })