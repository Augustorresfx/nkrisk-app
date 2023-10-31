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

# Importe de modelos
from .models import Cobranza

# Importe de librerias
import pandas as pd
import openpyxl
import xlwings as xw
class HomeView(View):
    def get(self, request, *args, **kwargs):
        context = {
            
        }
        return redirect('login')
    

@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request, *args, **kwargs):
        cobranzas = Cobranza.objects.all().order_by('-fecha_vencimiento')  # Obtener todas las instancias de Cobranza
        cobranzas_paginadas = Paginator(cobranzas, 30)
        page_number = request.GET.get("page")
        filter_pages = cobranzas_paginadas.get_page(page_number)
        context = {
            'cobranzas': cobranzas,  # Pasar las cobranzas al contexto
            'pages': filter_pages
        }
        return render(request, 'dashboard.html', context)
    def post(self, request, *args, **kwargs):
        if "delete_data" in request.POST:
            Cobranza.objects.all().delete()  # Elimina todos los registros de Cobranza
            return redirect('dashboard')

        file1 = request.FILES.get('file1')
        workbook = openpyxl.load_workbook(file1)
        sheet = workbook.active

        # Itera a través de las filas del archivo Excel y guarda los datos en la base de datos
        for row in sheet.iter_rows(min_row=4, values_only=True):
            asegurador, riesgo, productor, cliente, poliza, endoso, cuota, fecha_vencimiento, moneda, importe, saldo, forma_pago, factura = row
            fecha_vencimiento = fecha_vencimiento.replace("/", "-")
            
            fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%d-%m-%Y").strftime("%Y-%m-%d")
            Cobranza.objects.create(
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
        
        context = {
            
        }

        return render(request, 'dashboard.html', context)


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
            cobranzas = Cobranza.objects.filter(fecha_vencimiento__gte=start_date, fecha_vencimiento__lt=end_date).order_by('-fecha_vencimiento')
        else:
            # Si no se selecciona un mes, muestra todas las cobranzas
            cobranzas = Cobranza.objects.all().order_by('-fecha_vencimiento')
        
        cobranzas_paginadas = Paginator(cobranzas, 30)
        page_number = request.GET.get("page")
        filter_pages = cobranzas_paginadas.get_page(page_number)
        context = {
            'cobranzas': cobranzas,  # Pasar las cobranzas al contexto
            'pages': filter_pages
        }
        return render(request, 'cobranzas/cobranzas.html', context)
    
    
    def post(self, request, *args, **kwargs):
        if "delete_data" in request.POST:
            Cobranza.objects.all().delete()  # Elimina todos los registros de Cobranza
            return redirect('cobranzas')
        
        
        selected_month = int(request.POST.get('month'))
        selected_year = int(request.POST.get('year'))
        file1 = request.FILES.get('file1')
        workbook = openpyxl.load_workbook(file1)
        sheet = workbook.active

        data = []  # Lista para almacenar las filas
        for row in sheet.iter_rows(min_row=4, values_only=True):
            asegurador, riesgo, productor, cliente, poliza, endoso, cuota, fecha_vencimiento, moneda, importe, saldo, forma_pago, factura = row
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
            fecha_vencimiento = fecha_vencimiento.replace("/", "-")
            
            fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%d-%m-%Y")
            
            if fecha_vencimiento.month == selected_month and fecha_vencimiento.year == selected_year:
                Cobranza.objects.create(
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



class SignOutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')

class SignInView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('cobranzas')
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
                return redirect('cobranzas')
        
        return render(request, 'login.html', {
            'form': form,
            'error': 'El nombre de usuario o la contraseña no existen',
        })