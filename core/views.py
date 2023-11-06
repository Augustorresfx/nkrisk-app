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

# Importe de formularios
from .forms import VehiculoForm

# Importe de modelos
from .models import Vencimiento, Flota, Vehiculo

# Importe de librerias
import pandas as pd
import openpyxl
import xlwings as xw
class HomeView(View):
    def get(self, request, *args, **kwargs):
        context = {
            
        }
        return redirect('login')

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

        return render(request, 'cobranzas/cobranzas.html', context)
    
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

        return render(request, 'vencimientos/vencimientos.html', context)
    
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
                return redirect('vencimientos')
        
        return render(request, 'login.html', {
            'form': form,
            'error': 'El nombre de usuario o la contraseña no existen',
        })