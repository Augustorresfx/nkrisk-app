import pandas as pd
from django.db.models import Sum
from .models import CoberturaNominada, CoberturaInnominada, ProrrogaSolicitada
from django.db.models import Q
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import numpy as np


import logging

# Configurar el logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler('errores_importacion.log')  # Registra en un archivo de log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def cargar_datos_nominados(df, asegurado):
    for index, row in df.iterrows():
        # Procesar vigencia_desde
        if row['Vigencia Desde'].strip().lower() != "indefinida":
            vigencia_desde = datetime.strptime(row['Vigencia Desde'], "%d/%m/%Y").strftime("%Y-%m-%d")
        else:
            vigencia_desde = "Indefinida"
        
        # Procesar vigencia_hasta
        if row['Vigencia Hasta'].strip().lower() != "indefinida":
            vigencia_hasta = datetime.strptime(row['Vigencia Hasta'], "%d/%m/%Y").strftime("%Y-%m-%d")
        else:
            vigencia_hasta = "Indefinida"
        
        # Procesar Monto Temporal para que no sea nan
        if np.isnan(row['Monto Temporal']):
            monto_temporal = 0
        else: 
            monto_temporal = row['Monto Temporal']
            
        # Procesar Cobertura para que no sea nan
        if np.isnan(row['Cobertura %']):
            cobertura = 0
        else: 
            cobertura = row['Cobertura %']
        
        # Crear la instancia del modelo
        CoberturaNominada.objects.create(
            asegurado=asegurado,
            id_nacional=row['Id. Nacional'],
            pais=row['País'],
            ciudad=row['Ciudad'],
            cliente=row['Cliente'],
            vigencia_desde=vigencia_desde,
            vigencia_hasta=vigencia_hasta,
            moneda=row['Moneda'],
            monto_solicitado=row['Monto Solicitado'],
            monto_aprobado=row['Monto Aprobado'],
            estado=row['Estado'],
            monto_temporal=monto_temporal,
            cobertura=cobertura,
            condicion_de_venta=row['Condición de Venta'],
            linea_de_negocios=row['Línea de  Negocios'],
            plazo_en_dias=row['Plazo [días]'],
            codigoAsegurado=row['Código Asegurado'],
            observaciones=row['Observaciones']
        )

def cargar_datos_innominados(df, asegurado):
    # Convertir fechas al formato correcto, manejando valores vacíos
    df['Fecha1era Consulta'] = pd.to_datetime(df['Fecha1era Consulta'], format='%d/%m/%Y', errors='coerce')
    df['Fecha Última Consulta'] = pd.to_datetime(df['Fecha Última Consulta'], format='%d/%m/%Y', errors='coerce')
    df['Fecha Hasta'] = pd.to_datetime(df['Fecha Hasta'], format='%d-%m-%Y', errors='coerce')

    for index, row in df.iterrows():
        # Asegurarnos de que las fechas se formatean correctamente si no son nulas
        fecha_primer_consulta_formateada = row['Fecha1era Consulta'].strftime('%Y-%m-%d') if pd.notnull(row['Fecha1era Consulta']) else None
        fecha_ultima_consulta_formateada = row['Fecha Última Consulta'].strftime('%Y-%m-%d') if pd.notnull(row['Fecha Última Consulta']) else None
        fecha_hasta_formateada = row['Fecha Hasta'].strftime('%Y-%m-%d') if pd.notnull(row['Fecha Hasta']) else None

        # Crear la instancia del modelo
        CoberturaInnominada.objects.create(
            asegurado=asegurado,
            id_nacional=row['Id. Nacional'],
            nombre_cliente=row['Cliente'],
            fecha_primer_consulta=fecha_primer_consulta_formateada,
            fecha_ultima_consulta=fecha_ultima_consulta_formateada,
            fecha_hasta=fecha_hasta_formateada,
            estado_actual=row['EstadoActual'],
            codigo_autorizacion=row['CódigoAutorización'],
            codigoAsegurado=row['CódigoAsegurado'],
        )

def cargar_datos_prorrogas(df, asegurado):
    
    # Convertir fechas al formato correcto
    df['Fecha  Recepción'] = pd.to_datetime(df['Fecha  Recepción'], format='%d-%m-%Y', errors='coerce')
    df['F.Emisión Factura'] = pd.to_datetime(df['F.Emisión Factura'], format='%d/%m/%Y', errors='coerce')
    df['F.Vencimiento Factura'] = pd.to_datetime(df['F.Vencimiento Factura'], format='%d/%m/%Y', errors='coerce')
    df['F.Prórroga Solicitada'] = pd.to_datetime(df['F.Prórroga Solicitada'], format='%d/%m/%Y', errors='coerce')
    df['F.Vencimiento Prórroga'] = pd.to_datetime(df['F.Vencimiento Prórroga'], format='%d/%m/%Y', errors='coerce')
    
    for index, row in df.iterrows():
        fecha_recepcion_formateada = row['Fecha  Recepción'].strftime('%Y-%m-%d') if pd.notnull(row['Fecha  Recepción']) else None
        fecha_emision_factura_formateada = row['F.Emisión Factura'].strftime('%Y-%m-%d') if pd.notnull(row['F.Emisión Factura']) else None
        fecha_vencimiento_factura_formateada = row['F.Vencimiento Factura'].strftime('%Y-%m-%d') if pd.notnull(row['F.Vencimiento Factura']) else None
        fecha_prorroga_solicitada_formateada = row['F.Prórroga Solicitada'].strftime('%Y-%m-%d') if pd.notnull(row['F.Prórroga Solicitada']) else None
        fecha_vencimiento_prorroga_formateada = row['F.Vencimiento Prórroga'].strftime('%Y-%m-%d') if pd.notnull(row['F.Vencimiento Prórroga']) else None
        
        ProrrogaSolicitada.objects.create(
            asegurado=asegurado,
            num_solicitud = row['Número  Solicitud'],
            fecha_recepcion = fecha_recepcion_formateada,
            cliente = row['Cliente'],
            id_nacional = row['Id. Nacional'],
            factura = row['Factura'],
            fecha_emision_factura = fecha_emision_factura_formateada,
            fecha_vencimiento_factura = fecha_vencimiento_factura_formateada,
            fecha_prorroga_solicitada = fecha_prorroga_solicitada_formateada,
            fecha_vencimiento_prorroga = fecha_vencimiento_prorroga_formateada,
            moneda = row['Mon.'],
            monto_factura = row['Monto Factura'],
            saldo_prorroga = row['Saldo  Prórroga'],
            estado = row['Estado'],
            observacion = row['Observación'],
            pagador = row['Pagador'],
        )
        

def consultar_por_divisiones(fecha, asegurado):
    # Convertir la fecha de entrada a un objeto datetime
    fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")
 
    # Formatear las fechas en YYYY-MM-DD (no es correcta la comparación en el formato DD-MM-YYYY "15-01-2024" sería mayor que "05-02-2023)
    fecha_formateada = fecha_dt.strftime("%Y-%m-%d")
    # Filtrar coberturas rechazadas y aprobadas
    sol_de_cobertura_rechaz = CoberturaNominada.objects.filter(
        vigencia_desde=fecha_formateada,
        estado='RECHAZ',
        asegurado=asegurado,
    )
    sol_de_cobertura_aprob = CoberturaNominada.objects.filter(
        vigencia_desde=fecha_formateada,
        estado='ACTIVA',
        asegurado=asegurado,
    )
    tiene_codigo_asegurado = (
        sol_de_cobertura_rechaz.filter(
            Q(codigoAsegurado__isnull=False) & 
            ~Q(codigoAsegurado='') & 
            ~Q(codigoAsegurado=np.nan)
        ).exists() or 
        sol_de_cobertura_aprob.filter(
            Q(codigoAsegurado__isnull=False) & 
            ~Q(codigoAsegurado='') & 
            ~Q(codigoAsegurado=np.nan)
        ).exists()
    )
    
    if tiene_codigo_asegurado:
        return True
    else:
        return False
        
# PRIMER TABLA - Solicitudes de cobertura
def obtener_datos_solicitudes_cobertura(fecha, asegurado):
    # Convertir la fecha de entrada a un objeto datetime
    fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")
 
    # Formatear las fechas en YYYY-MM-DD (no es correcta la comparación en el formato DD-MM-YYYY "15-01-2024" sería mayor que "05-02-2023)
    fecha_formateada = fecha_dt.strftime("%Y-%m-%d")
    
    # Obtener el primer día del mes de entrada
    primer_dia_mes = fecha_dt.replace(day=1)

    # Obtener el último día del mes de entrada de manera segura
    ultimo_dia_mes = primer_dia_mes.replace(day=calendar.monthrange(primer_dia_mes.year, primer_dia_mes.month)[1])

 
    # Formatear las fechas en YYYY-MM-DD (no es correcta la comparación en el formato DD-MM-YYYY "15-01-2024" sería mayor que "05-02-2023)
    fecha_primer_dia_mes = primer_dia_mes.strftime("%Y-%m-%d")
    fecha_ultimo_dia_mes = ultimo_dia_mes.strftime("%Y-%m-%d")
    
    # Filtrar coberturas rechazadas y aprobadas
    sol_de_cobertura_rechaz = CoberturaNominada.objects.filter(
        vigencia_desde__gte=fecha_primer_dia_mes,
        vigencia_desde__lte=fecha_ultimo_dia_mes,
        estado='RECHAZ',
        asegurado=asegurado,
    )
    sol_de_cobertura_aprob = CoberturaNominada.objects.filter(
        vigencia_desde__gte=fecha_primer_dia_mes,
        vigencia_desde__lte=fecha_ultimo_dia_mes,
        estado='ACTIVA',
        asegurado=asegurado,
    )
    
    # Verificar si alguna cobertura tiene un código de asegurado que no sea nulo, vacío o NaN
    tiene_codigo_asegurado = (
        sol_de_cobertura_rechaz.filter(
            Q(codigoAsegurado__isnull=False) & 
            ~Q(codigoAsegurado='') & 
            ~Q(codigoAsegurado=np.nan)
        ).exists() or 
        sol_de_cobertura_aprob.filter(
            Q(codigoAsegurado__isnull=False) & 
            ~Q(codigoAsegurado='') & 
            ~Q(codigoAsegurado=np.nan)
        ).exists()
    )
    print("SOLICITUDES DE COBERTURA 1ER TABLA (TIENE DIVISIONES): ", tiene_codigo_asegurado)
    # Si tiene código de asegurado, hacemos la división entre envases y cartulinas
    if tiene_codigo_asegurado:
        # Divisiones de rechazadas y aprobadas
        sol_envases_rechaz = sol_de_cobertura_rechaz.filter(codigoAsegurado__startswith='100')
        sol_cartulinas_rechaz = sol_de_cobertura_rechaz.filter(codigoAsegurado__startswith='200')
        sol_envases_aprob = sol_de_cobertura_aprob.filter(codigoAsegurado__startswith='100')
        sol_cartulinas_aprob = sol_de_cobertura_aprob.filter(codigoAsegurado__startswith='200')

        # Cálculos para "envases"
        num_cobertura_rechaz_envases = sol_envases_rechaz.count()
        num_cobertura_aprob_envases = sol_envases_aprob.count()
        num_total_cobertura_envases = num_cobertura_rechaz_envases + num_cobertura_aprob_envases
        cant_solicitado_rechaz_envases = sol_envases_rechaz.aggregate(total=Sum('monto_solicitado'))['total'] or 0
        cant_solicitado_aprob_envases = sol_envases_aprob.aggregate(total=Sum('monto_solicitado'))['total'] or 0
        total_solicitado_envases = cant_solicitado_rechaz_envases + cant_solicitado_aprob_envases
        cant_aprobado_aprob_envases = sol_envases_aprob.aggregate(total=Sum('monto_aprobado'))['total'] or 0

        porcentaje_aprob_envases = 0
        if cant_solicitado_aprob_envases != 0:
            porcentaje_aprob_envases = round((cant_aprobado_aprob_envases / cant_solicitado_aprob_envases) * 100)

        porcentaje_total_aprob_envases = 0
        if total_solicitado_envases != 0:
            porcentaje_total_aprob_envases = round((cant_aprobado_aprob_envases / total_solicitado_envases) * 100)

        # Cálculos para "cartulinas"
        num_cobertura_rechaz_cartulinas = sol_cartulinas_rechaz.count()
        num_cobertura_aprob_cartulinas = sol_cartulinas_aprob.count()
        num_total_cobertura_cartulinas = num_cobertura_rechaz_cartulinas + num_cobertura_aprob_cartulinas
        cant_solicitado_rechaz_cartulinas = sol_cartulinas_rechaz.aggregate(total=Sum('monto_solicitado'))['total'] or 0
        cant_solicitado_aprob_cartulinas = sol_cartulinas_aprob.aggregate(total=Sum('monto_solicitado'))['total'] or 0
        total_solicitado_cartulinas = cant_solicitado_rechaz_cartulinas + cant_solicitado_aprob_cartulinas
        cant_aprobado_aprob_cartulinas = sol_cartulinas_aprob.aggregate(total=Sum('monto_aprobado'))['total'] or 0

        porcentaje_aprob_cartulinas = 0
        if cant_solicitado_aprob_cartulinas != 0:
            porcentaje_aprob_cartulinas = round((cant_aprobado_aprob_cartulinas / cant_solicitado_aprob_cartulinas) * 100)

        porcentaje_total_aprob_cartulinas = 0
        if total_solicitado_cartulinas != 0:
            porcentaje_total_aprob_cartulinas = round((cant_aprobado_aprob_cartulinas / total_solicitado_cartulinas) * 100)

        return {
            # Envases
            'sol_envases_aprob': sol_envases_aprob,
            'sol_envases_rechaz': sol_envases_rechaz,
            'num_cobertura_rechaz_envases': num_cobertura_rechaz_envases,
            'num_cobertura_aprob_envases': num_cobertura_aprob_envases,
            'num_total_cobertura_envases': num_total_cobertura_envases,
            'cant_solicitado_rechaz_envases': cant_solicitado_rechaz_envases,
            'cant_solicitado_aprob_envases': cant_solicitado_aprob_envases,
            'total_solicitado_envases': total_solicitado_envases,
            'cant_aprobado_aprob_envases': cant_aprobado_aprob_envases,
            'porcentaje_aprob_envases': porcentaje_aprob_envases,
            'porcentaje_total_aprob_envases': porcentaje_total_aprob_envases,

            # Cartulinas
            'sol_cartulinas_aprob': sol_cartulinas_aprob,
            'sol_cartulinas_rechaz': sol_cartulinas_rechaz,
            'num_cobertura_rechaz_cartulinas': num_cobertura_rechaz_cartulinas,
            'num_cobertura_aprob_cartulinas': num_cobertura_aprob_cartulinas,
            'num_total_cobertura_cartulinas': num_total_cobertura_cartulinas,
            'cant_solicitado_rechaz_cartulinas': cant_solicitado_rechaz_cartulinas,
            'cant_solicitado_aprob_cartulinas': cant_solicitado_aprob_cartulinas,
            'total_solicitado_cartulinas': total_solicitado_cartulinas,
            'cant_aprobado_aprob_cartulinas': cant_aprobado_aprob_cartulinas,
            'porcentaje_aprob_cartulinas': porcentaje_aprob_cartulinas,
            'porcentaje_total_aprob_cartulinas': porcentaje_total_aprob_cartulinas,
        }

    # Si no hay códigos de asegurado, retorna los valores originales sin distinción de divisiones
    num_cobertura_rechaz = sol_de_cobertura_rechaz.count()
    num_cobertura_aprob = sol_de_cobertura_aprob.count()
    num_total_cobertura = num_cobertura_rechaz + num_cobertura_aprob
    cant_solicitado_rechaz = sol_de_cobertura_rechaz.aggregate(total=Sum('monto_solicitado'))['total'] or 0
    cant_solicitado_aprob = sol_de_cobertura_aprob.aggregate(total=Sum('monto_solicitado'))['total'] or 0
    cant_solicitado_aprob = float(cant_solicitado_aprob)
    total_solicitado = cant_solicitado_rechaz + cant_solicitado_aprob
    cant_aprobado_aprob = sol_de_cobertura_aprob.aggregate(total=Sum('monto_aprobado'))['total'] or 0
    
    porcentaje_aprob = 0
    if cant_solicitado_aprob != 0:
        porcentaje_aprob = round((cant_aprobado_aprob / cant_solicitado_aprob) * 100)

    porcentaje_total_aprob = 0
    if total_solicitado != 0:
        porcentaje_total_aprob = round((cant_aprobado_aprob / total_solicitado) * 100)
    print(cant_solicitado_aprob)
    return {
        'sol_sin_separacion_aprob': sol_de_cobertura_aprob,
        'sol_sin_separacion_rechaz': sol_de_cobertura_rechaz,
        'num_cobertura_rechaz': num_cobertura_rechaz,
        'num_cobertura_aprob': num_cobertura_aprob,
        'num_total_cobertura': num_total_cobertura,
        'cant_solicitado_rechaz': cant_solicitado_rechaz,
        'cant_solicitado_aprob': cant_solicitado_aprob,
        'total_solicitado': total_solicitado,
        'cant_aprobado_aprob': cant_aprobado_aprob,
        'porcentaje_aprob': porcentaje_aprob,
        'porcentaje_total_aprob': porcentaje_total_aprob,
    }
    
# SEGUNDA TABLA - Clientes sin cobertura
def obtener_datos_clientes_sin_cobertura(fecha, asegurado):
    # Convierte la fecha de entrada a un objeto datetime
    fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")

    # Formatear la fecha en YYYY-MM-DD (no es correcta la comparación en el formato DD-MM-YYYY "15-01-2024" sería mayor que "05-02-2023)
    fecha_formateada = fecha_dt.strftime("%Y-%m-%d")

    # Obtener el primer día del mes anterior
    fecha_un_mes_anterior_dt = (fecha_dt - relativedelta(months=1)).replace(day=1)
    
    # Formatear las fechas en YYYY-MM-DD (no es correcta la comparación en el formato DD-MM-YYYY "15-01-2024" sería mayor que "05-02-2023)
    fecha_un_mes_anterior = fecha_un_mes_anterior_dt.strftime("%Y-%m-%d")
   
    # Traer los CUITs (id_nacional) de los clientes que tienen coberturas activas o expiradas (para excluirlos)
    id_nacional_con_cobertura_anterior = CoberturaNominada.objects.filter(
        Q(estado='ACTIVA') | Q(estado='EXPIRA'),
        vigencia_desde__lt=fecha_un_mes_anterior,
        asegurado=asegurado
    ).values_list('id_nacional', flat=True)

    # Verificar si el asegurado tiene cobertura innominada
    id_nacional_inominados = []
    if CoberturaInnominada.objects.filter(asegurado=asegurado).exists():
        id_nacional_inominados = CoberturaInnominada.objects.filter(
            asegurado=asegurado
        ).values_list('id_nacional', flat=True)

    # Filtrar las solicitudes de cobertura aprobadas (ACTIVA) y rechazadas (RECHAZ) cuya id_nacional no esté en las listas anteriores
    clientes_nuevos_aprob = CoberturaNominada.objects.filter(
        vigencia_desde=fecha_formateada,
        estado='ACTIVA',
        asegurado=asegurado,
    ).exclude(id_nacional__in=id_nacional_con_cobertura_anterior).exclude(id_nacional__in=id_nacional_inominados)

    clientes_nuevos_rechaz = CoberturaNominada.objects.filter(
        vigencia_desde=fecha_formateada,
        estado='RECHAZ',
        asegurado=asegurado,
    ).exclude(id_nacional__in=id_nacional_con_cobertura_anterior).exclude(id_nacional__in=id_nacional_inominados)

    # Verificar si alguna cobertura tiene un código de asegurado que no sea nulo, vacío o NaN
    tiene_codigo_asegurado = consultar_por_divisiones(fecha, asegurado)
    
    # Si tiene código de asegurado, hacemos la división entre envases y cartulinas
    if tiene_codigo_asegurado:
        # Divisiones de rechazadas y aprobadas
        sol_envases_rechaz = clientes_nuevos_rechaz.filter(codigoAsegurado__startswith='100')
        sol_cartulinas_rechaz = clientes_nuevos_rechaz.filter(codigoAsegurado__startswith='200')

        sol_envases_aprob = clientes_nuevos_aprob.filter(codigoAsegurado__startswith='100')
        sol_cartulinas_aprob = clientes_nuevos_aprob.filter(codigoAsegurado__startswith='200')

        # Cálculos para envases
        num_envases_rechaz = sol_envases_rechaz.count()
        num_envases_aprob = sol_envases_aprob.count()
        num_envases_total = num_envases_aprob + num_envases_rechaz
        cant_solicitado_envases_rechaz = sol_envases_rechaz.aggregate(total=Sum('monto_solicitado'))['total'] or 0
        cant_solicitado_envases_aprob = sol_envases_aprob.aggregate(total=Sum('monto_solicitado'))['total'] or 0
        total_solicitado_envases = cant_solicitado_envases_rechaz + cant_solicitado_envases_aprob
        cant_aprobado_envases_aprob = sol_envases_aprob.aggregate(total=Sum('monto_aprobado'))['total'] or 0
        
        porcentaje_envases_aprob = 0
        if cant_solicitado_envases_aprob != 0:
            porcentaje_envases_aprob = round((cant_aprobado_envases_aprob / cant_solicitado_envases_aprob) * 100)
       
        porcentaje_total_aprob_envases = 0
        if total_solicitado_envases != 0:
            porcentaje_total_aprob_envases = round((cant_aprobado_envases_aprob / total_solicitado_envases) * 100)
       
        # Cálculos para cartulinas
        num_cartulinas_rechaz = sol_cartulinas_rechaz.count()
        num_cartulinas_aprob = sol_cartulinas_aprob.count()
        num_cartulinas_total = num_cartulinas_aprob + num_cartulinas_rechaz
        cant_solicitado_cartulinas_rechaz = sol_cartulinas_rechaz.aggregate(total=Sum('monto_solicitado'))['total'] or 0
        cant_solicitado_cartulinas_aprob = sol_cartulinas_aprob.aggregate(total=Sum('monto_solicitado'))['total'] or 0
        total_solicitado_cartulinas = cant_solicitado_cartulinas_rechaz + cant_solicitado_cartulinas_aprob
        cant_aprobado_cartulinas_aprob = sol_cartulinas_aprob.aggregate(total=Sum('monto_aprobado'))['total'] or 0
        
        porcentaje_cartulinas_aprob = 0
        if cant_solicitado_cartulinas_aprob != 0:
            porcentaje_cartulinas_aprob = round((cant_aprobado_cartulinas_aprob / cant_solicitado_cartulinas_aprob) * 100)

        porcentaje_total_aprob_cartulinas = 0
        if total_solicitado_cartulinas != 0:
            porcentaje_total_aprob_cartulinas = round((cant_aprobado_cartulinas_aprob / total_solicitado_cartulinas) * 100)
        return {
            'envases': {
                'sol_envases_aprob': sol_envases_aprob,
                'sol_envases_rechaz': sol_envases_rechaz,
                'num_total_cobertura_envases': num_envases_total,
                'num_cobertura_rechaz': num_envases_rechaz,
                'num_cobertura_aprob': num_envases_aprob,
                'cant_solicitado_rechaz': cant_solicitado_envases_rechaz,
                'cant_solicitado_aprob': cant_solicitado_envases_aprob,
                'total_solicitado': total_solicitado_envases,
                'cant_aprobado_aprob': cant_aprobado_envases_aprob,
                'porcentaje_aprob': porcentaje_envases_aprob,
                'porcentaje_total_aprob_envases': porcentaje_total_aprob_envases,
            },
            'cartulinas': {
                'sol_cartulinas_aprob': sol_cartulinas_aprob,
                'sol_cartulinas_rechaz': sol_cartulinas_rechaz,
                'num_total_cobertura_cartulinas': num_cartulinas_total,
                'num_cobertura_rechaz': num_cartulinas_rechaz,
                'num_cobertura_aprob': num_cartulinas_aprob,
                'cant_solicitado_rechaz': cant_solicitado_cartulinas_rechaz,
                'cant_solicitado_aprob': cant_solicitado_cartulinas_aprob,
                'total_solicitado': total_solicitado_cartulinas,
                'cant_aprobado_aprob': cant_aprobado_cartulinas_aprob,
                'porcentaje_aprob': porcentaje_cartulinas_aprob,
                'porcentaje_total_aprob_cartulinas': porcentaje_total_aprob_cartulinas,
            }
        }

    # Si no hay códigos asegurados (200 o 100), no hacemos divisiones
    else:
        num_cobertura_rechaz = clientes_nuevos_rechaz.count()
        num_cobertura_aprob = clientes_nuevos_aprob.count()
        num_total_cobertura = num_cobertura_rechaz + num_cobertura_aprob
        cant_solicitado_rechaz = clientes_nuevos_rechaz.aggregate(total=Sum('monto_solicitado'))['total'] or 0
        cant_solicitado_aprob = clientes_nuevos_aprob.aggregate(total=Sum('monto_solicitado'))['total'] or 0
        total_solicitado = cant_solicitado_rechaz + cant_solicitado_aprob
        cant_aprobado_aprob = clientes_nuevos_aprob.aggregate(total=Sum('monto_aprobado'))['total'] or 0
        
        porcentaje_aprob = 0
        if cant_solicitado_aprob != 0:
            porcentaje_aprob = round((cant_aprobado_aprob / cant_solicitado_aprob) * 100)

        porcentaje_total_aprob = 0
        if total_solicitado != 0:
            porcentaje_total_aprob = round((cant_aprobado_aprob / total_solicitado) * 100)
        
        return {
            'sol_sin_separacion_aprob': clientes_nuevos_aprob,
            'sol_sin_separacion_rechaz': clientes_nuevos_rechaz,
            'num_cobertura_rechaz': num_cobertura_rechaz,
            'num_cobertura_aprob': num_cobertura_aprob,
            'num_total_cobertura': num_total_cobertura,
            'cant_solicitado_rechaz': cant_solicitado_rechaz,
            'cant_solicitado_aprob': cant_solicitado_aprob,
            'total_solicitado': total_solicitado,
            'cant_aprobado_aprob': cant_aprobado_aprob,
            'porcentaje_aprob': porcentaje_aprob,
            'porcentaje_total_aprob': porcentaje_total_aprob,
        }
    
# TERCER TABLA - Reestudios (Solicitudes de Aumento)
def obtener_datos_reestudios(fecha, asegurado):
    # Convertir la fecha de entrada a un objeto datetime
    fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")

    # Obtener el primer día y el último día del mes que se pide
    primer_dia_mes = fecha_dt.replace(day=1)
    ultimo_dia_mes = primer_dia_mes.replace(day=calendar.monthrange(primer_dia_mes.year, primer_dia_mes.month)[1])

    # Formatear las fechas para consulta
    fecha_primer_dia_mes = primer_dia_mes.strftime("%Y-%m-%d")
    fecha_ultimo_dia_mes = ultimo_dia_mes.strftime("%Y-%m-%d")
    
    # Obtener el primer día del mes anterior
    fecha_un_mes_anterior_dt = (fecha_dt - relativedelta(months=1)).replace(day=1)
    
    # Formatear las fechas en YYYY-MM-DD (no es correcta la comparación en el formato DD-MM-YYYY "15-01-2024" sería mayor que "05-02-2023)
    fecha_un_mes_anterior = fecha_un_mes_anterior_dt.strftime("%Y-%m-%d")

    # Función para obtener los id_nacional y vigencia_desde de las solicitudes activas anteriores al mes ingresado
    def id_nacional_con_cobertura_activa(codigo=None):
        
        filtro_base = CoberturaNominada.objects.filter(
            estado='ACTIVA',
            vigencia_desde__lte=fecha_un_mes_anterior,
            asegurado=asegurado
        )

        # Si se proporciona un código, filtrar por los primeros tres dígitos del codigoAsegurado
        if codigo:
            filtro_base = filtro_base.filter(codigoAsegurado__startswith=codigo)

        # Devolver los id_nacional y las vigencias de las solicitudes "REEMPL"
        return filtro_base.values_list('id_nacional', 'vigencia_desde', 'monto_aprobado', 'monto_solicitado')


    # Función para filtrar y calcular los datos por código asegurado o sin código
    def filtrar_por_codigo(codigo=None):
        # Obtener los id_nacional, las fechas de vigencia_desde y el monto aprobado de las solicitudes "REEMPL"
        id_nacional_y_vigencia_activa = id_nacional_con_cobertura_activa(codigo)

        reestudios_aprob = []
        reestudios_rechaz = []
        
        # Variables usadas para guardar montos anteriores
        
        cant_anterior_aprob = 0
        cant_anterior_rechaz = 0
        cant_anterior_total = 0
        
        # Para cada id_nacional y vigencia desde, buscar las solicitudes activas y rechazadas
        for id_nacional, vigencia_desde, monto_reempl, monto_sol_anterior in id_nacional_y_vigencia_activa:
            # Buscar la solicitud con estado "ACTIVA" (reestudio aprobado) y con monto solicitado mayor al anterior
            solicitud_aprob = CoberturaNominada.objects.filter(
                id_nacional=id_nacional,
                vigencia_desde__gte=fecha_primer_dia_mes,
                vigencia_desde__lte=fecha_ultimo_dia_mes,
                estado='ACTIVA',
                monto_solicitado__gt=monto_sol_anterior
            ).first()

            # Buscar la solicitud con estado "RECHAZ" (reestudio rechazado) y con monto solicitado mayor al anterior
            solicitud_rechaz = CoberturaNominada.objects.filter(
                id_nacional=id_nacional,
                vigencia_desde__gte=fecha_primer_dia_mes,
                vigencia_desde__lte=fecha_ultimo_dia_mes,
                estado='RECHAZ',
                monto_solicitado__gt=monto_sol_anterior
            ).first()

            # Si hay una solicitud aprobada y su monto aprobado es mayor que el de "REEMPL", agregarla a la lista de reestudios aprobados
            if solicitud_aprob and solicitud_aprob.monto_solicitado > monto_sol_anterior:
                solicitud_aprob.monto_anterior = monto_reempl
                reestudios_aprob.append(solicitud_aprob)
                # Sumo al total, el monto de la solicitud que fue reemplazada
                cant_anterior_aprob += monto_reempl

            # Si hay una solicitud rechazada, agregarla a la lista de reestudios rechazados
            if solicitud_rechaz:
                print(f"DEBUG: monto_reempl={monto_reempl} (type: {type(monto_reempl)})")
                solicitud_rechaz.monto_anterior = monto_reempl
                reestudios_rechaz.append(solicitud_rechaz)
                # Sumo al total, el monto de la solicitud que fue reemplazada
                cant_anterior_rechaz += monto_reempl

        # Cálculos y agregados
        
        cant_anterior_total = cant_anterior_aprob + cant_anterior_rechaz
        
        num_reestudios_aprob = len(reestudios_aprob)
        num_reestudios_rechaz = len(reestudios_rechaz)
        num_total_reestudios = num_reestudios_aprob + num_reestudios_rechaz

        cant_solicitado_aprob = sum(solicitud.monto_solicitado for solicitud in reestudios_aprob)
        cant_solicitado_rechaz = sum(solicitud.monto_solicitado for solicitud in reestudios_rechaz)
        total_solicitado = cant_solicitado_aprob + cant_solicitado_rechaz
        
        cant_aprobado_aprob = sum(solicitud.monto_aprobado for solicitud in reestudios_aprob)

        porcentaje_aprob = 0
        if cant_solicitado_aprob != 0:
            porcentaje_aprob = round((cant_aprobado_aprob / cant_solicitado_aprob) * 100)

        porcentaje_total_aprob = 0
        if total_solicitado != 0:
            porcentaje_total_aprob = round((cant_aprobado_aprob / total_solicitado) * 100)

        return {
            'reestudios_aprob': reestudios_aprob,
            'reestudios_rechaz': reestudios_rechaz,
            'num_reestudios_aprob': num_reestudios_aprob,
            'num_reestudios_rechaz': num_reestudios_rechaz,
            'num_total_reestudios': num_total_reestudios,
            'cant_solicitado_aprob': cant_solicitado_aprob,
            'cant_solicitado_rechaz': cant_solicitado_rechaz,
            'total_solicitado': total_solicitado,
            'cant_aprobado_aprob': cant_aprobado_aprob,
            'porcentaje_aprob': porcentaje_aprob,
            'porcentaje_total_aprob': porcentaje_total_aprob,
            'cant_anterior_aprob': cant_anterior_aprob,
            'cant_anterior_rechaz': cant_anterior_rechaz,
            'cant_anterior_total': cant_anterior_total,
        }

    # Verificar si alguna solicitud de cobertura tiene codigoAsegurado para este asegurado
    existe_codigo_asegurado = CoberturaNominada.objects.filter(
        asegurado=asegurado,
        codigoAsegurado__isnull=False
    ).exists()

    if existe_codigo_asegurado:
        # Filtrar por código "Envases" (100)
        datos_envases = filtrar_por_codigo('100')

        # Filtrar por código "Cartulinas" (200)
        datos_cartulinas = filtrar_por_codigo('200')
    else:
        # Si no hay codigoAsegurado, no hacer separaciones por código
        datos_envases = None
        datos_cartulinas = None

    # Filtrar sin codigoAsegurado (incluye todos los asegurados sin código)
    datos_sin_separacion = filtrar_por_codigo()

    return {
        'envases': datos_envases,
        'cartulinas': datos_cartulinas,
        'sin_separacion': datos_sin_separacion
    }



# CUARTA TABLA - CANCELACIONES
def obtener_datos_cancelaciones(fecha, asegurado):
    # Convertir la fecha de entrada a un objeto datetime
    fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")

    # Obtener el primer día del mes de entrada
    primer_dia_mes = fecha_dt.replace(day=1)

    # Obtener el último día del mes de entrada de manera segura
    ultimo_dia_mes = primer_dia_mes.replace(day=calendar.monthrange(primer_dia_mes.year, primer_dia_mes.month)[1])

 
    # Formatear las fechas en YYYY-MM-DD (no es correcta la comparación en el formato DD-MM-YYYY "15-01-2024" sería mayor que "05-02-2023)
    fecha_primer_dia_mes = primer_dia_mes.strftime("%Y-%m-%d")
    fecha_ultimo_dia_mes = ultimo_dia_mes.strftime("%Y-%m-%d")
    # Función para obtener cancelaciones con o sin filtro por código
    def obtener_cancelaciones_por_codigo(codigo=None):

        # Filtrar por solicitudes canceladas
        cancelaciones = CoberturaNominada.objects.filter(
            estado='CANCEL',
            asegurado=asegurado,
            vigencia_hasta__gte=fecha_primer_dia_mes,
            vigencia_hasta__lte=fecha_ultimo_dia_mes,
        )
        
        # Si se proporciona un código, filtrar por los primeros tres dígitos del codigoAsegurado
        if codigo:
            cancelaciones = cancelaciones.filter(codigoAsegurado__startswith=codigo)

        # Obtener los datos de interés: cliente, id_nacional y monto_aprobado
        datos_cancelaciones = cancelaciones.values('cliente', 'id_nacional', 'monto_aprobado')

        # Calcular el número de cancelaciones
        num_cancelaciones = len(cancelaciones)

        # Calcular el total del monto aprobado
        total_monto_aprobado = cancelaciones.aggregate(total_monto_aprobado=Sum('monto_aprobado'))['total_monto_aprobado'] or 0

        return {
            'datos_cancelaciones': datos_cancelaciones,
            'num_cancelaciones': num_cancelaciones,
            'total_monto_aprobado': total_monto_aprobado
        }

    # Verificar si alguna solicitud de cobertura tiene codigoAsegurado para este asegurado
    existe_codigo_asegurado = CoberturaNominada.objects.filter(
        asegurado=asegurado,
        codigoAsegurado__isnull=False
    ).exists()

    if existe_codigo_asegurado:
        # Cancelaciones para "Envases" (código 100)
        cancelaciones_envases = obtener_cancelaciones_por_codigo('100')

        # Cancelaciones para "Cartulinas" (código 200)
        cancelaciones_cartulinas = obtener_cancelaciones_por_codigo('200')
    else:
        # Si no hay codigoAsegurado, no hacer separaciones por código
        cancelaciones_envases = None
        cancelaciones_cartulinas = None

    # Cancelaciones sin separación por códigoAsegurado
    cancelaciones_sin_separacion = obtener_cancelaciones_por_codigo()

    # Retornar los resultados
    return {
        'cancelaciones_envases': cancelaciones_envases,
        'cancelaciones_cartulinas': cancelaciones_cartulinas,
        'cancelaciones_sin_separacion': cancelaciones_sin_separacion
    }

# CUARTA TABLA - REDUCCIONES
def obtener_datos_reducciones(fecha, asegurado):
    # Convertimos la fecha de entrada a un objeto datetime
    fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")
    # Obtener el primer día y el último día del mes que se pide
    primer_dia_mes = fecha_dt.replace(day=1)
    ultimo_dia_mes = primer_dia_mes.replace(day=calendar.monthrange(primer_dia_mes.year, primer_dia_mes.month)[1])

    # Formatear las fechas para consulta
    fecha_primer_dia_mes = primer_dia_mes.strftime("%Y-%m-%d")
    fecha_ultimo_dia_mes = ultimo_dia_mes.strftime("%Y-%m-%d")
    
    # Obtener el primer día del mes anterior
    fecha_un_mes_anterior_dt = (fecha_dt - relativedelta(months=1)).replace(day=1)
    
    # Formatear las fechas en YYYY-MM-DD (no es correcta la comparación en el formato DD-MM-YYYY "15-01-2024" sería mayor que "05-02-2023)
    fecha_un_mes_anterior = fecha_un_mes_anterior_dt.strftime("%Y-%m-%d")

    # Función para obtener los id_nacional y vigencia_desde de las solicitudes activas anteriores al mes ingresado
    def id_nacional_con_cobertura_activa(codigo=None):
        
        filtro_base = CoberturaNominada.objects.filter(
            estado='ACTIVA',
            vigencia_desde__lte=fecha_primer_dia_mes,
            asegurado=asegurado
        )

        # Si se proporciona un código, filtrar por los primeros tres dígitos del codigoAsegurado
        if codigo:
            filtro_base = filtro_base.filter(codigoAsegurado__startswith=codigo)

        # Devolver los id_nacional y las vigencias de las solicitudes "REEMPL"
        return filtro_base

    solicitudes_activas = id_nacional_con_cobertura_activa()
    print(solicitudes_activas)
    
    reducciones_envases = []
    reducciones_cartulinas = []
    reducciones_sin_separacion = []
    num_reducciones_envases = 0
    num_reducciones_cartulinas = 0
    num_reducciones_sin_separacion = 0
    
    monto_aprob_reducciones_envases = 0
    monto_aprob_reducciones_cartulinas = 0
    monto_aprob_reducciones_sin_separacion = 0

    
    monto_anterior_reducciones_envases = 0
    monto_anterior_reducciones_cartulinas = 0
    monto_anterior_reducciones_sin_separacion = 0

    # Iterar sobre cada solicitud de reemplazo
    for solicitud_reempl in solicitudes_activas:
        # Buscar la solicitud activa que reemplaza la solicitud de reemplazo
        solicitud_activa = CoberturaNominada.objects.filter(
            asegurado=solicitud_reempl.asegurado,
            estado="ACTIVA",
            vigencia_desde__gte=fecha_primer_dia_mes,
            vigencia_desde__lte=fecha_ultimo_dia_mes,
            monto_solicitado__lt=solicitud_reempl.monto_solicitado,
            id_nacional = solicitud_reempl.id_nacional
        ).filter(
            Q(codigoAsegurado=solicitud_reempl.codigoAsegurado) | Q(id_nacional=solicitud_reempl.id_nacional)
        ).first()

        # Si se encuentra la solicitud activa y el monto es menor, es una reducción
        if solicitud_activa and solicitud_activa.monto_aprobado < solicitud_reempl.monto_aprobado:
            # Divisiones por tipo de código
            print(f"Solicitud reemplazo: {solicitud_reempl.monto_aprobado}, Solicitud activa: {solicitud_activa.monto_aprobado}")
            print(f"Solicitud reemplazo: {solicitud_reempl.monto_solicitado}, Solicitud activa: {solicitud_activa.monto_solicitado}")

            if solicitud_reempl.codigoAsegurado and solicitud_reempl.codigoAsegurado.startswith("100"):
                num_reducciones_envases += 1
                monto_aprob_reducciones_envases += solicitud_activa.monto_aprobado
                monto_anterior_reducciones_envases += solicitud_reempl.monto_aprobado
                reducciones_envases.append({
                    'cliente': solicitud_activa.cliente,
                    'id_nacional': solicitud_activa.id_nacional,
                    'monto_reduccion': solicitud_reempl.monto_aprobado - solicitud_activa.monto_aprobado,
                    'monto_aprobado': solicitud_activa.monto_aprobado,
                    'monto_anterior': solicitud_reempl.monto_aprobado
                
                })
            elif solicitud_reempl.codigoAsegurado and solicitud_reempl.codigoAsegurado.startswith("200"):
                num_reducciones_cartulinas += 1
                monto_aprob_reducciones_cartulinas += solicitud_activa.monto_aprobado
                monto_anterior_reducciones_cartulinas += solicitud_reempl.monto_aprobado
                reducciones_cartulinas.append({
                    'cliente': solicitud_activa.cliente,
                    'id_nacional': solicitud_activa.id_nacional,
                    'monto_reduccion': solicitud_reempl.monto_aprobado - solicitud_activa.monto_aprobado,
                    'monto_aprobado': solicitud_activa.monto_aprobado,
                    'monto_anterior': solicitud_reempl.monto_aprobado
                })
            else:
                num_reducciones_sin_separacion += 1
                monto_aprob_reducciones_sin_separacion += solicitud_activa.monto_aprobado
                monto_anterior_reducciones_sin_separacion += solicitud_reempl.monto_aprobado
                reducciones_sin_separacion.append({
                    'cliente': solicitud_activa.cliente,
                    'id_nacional': solicitud_activa.id_nacional,
                    'monto_reduccion': solicitud_reempl.monto_aprobado - solicitud_activa.monto_aprobado,
                    'monto_aprobado': solicitud_activa.monto_aprobado,
                    'monto_anterior': solicitud_reempl.monto_aprobado
                })


    
    # Retornar los resultados clasificados en las tres categorías
    return {
        'reducciones_envases': reducciones_envases,
        'reducciones_cartulinas': reducciones_cartulinas,
        'reducciones_sin_separacion': reducciones_sin_separacion,
        
        'num_reducciones_envases': num_reducciones_envases,
        'num_reducciones_cartulinas': num_reducciones_cartulinas,
        'num_reducciones_sin_separacion': num_reducciones_sin_separacion,
        
        'monto_aprob_reducciones_envases': monto_aprob_reducciones_envases,
        'monto_aprob_reducciones_cartulinas': monto_aprob_reducciones_cartulinas,
        'monto_aprob_reducciones_sin_separacion': monto_aprob_reducciones_sin_separacion,
        
        'monto_anterior_reducciones_envases': monto_anterior_reducciones_envases,
        'monto_anterior_reducciones_cartulinas': monto_anterior_reducciones_cartulinas,
        'monto_anterior_reducciones_sin_separacion': monto_anterior_reducciones_sin_separacion,
        
        
    }
    
# QUINTA TABLA - PRÓRROGAS SOLICITADAS
def obtener_datos_prorrogas(fecha, asegurado):
    # Convertimos la fecha de entrada a un objeto datetime
    fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")
    # Obtener el primer día y el último día del mes que se pide
    primer_dia_mes = fecha_dt.replace(day=1)
    ultimo_dia_mes = primer_dia_mes.replace(day=calendar.monthrange(primer_dia_mes.year, primer_dia_mes.month)[1])

    # Formatear las fechas para consulta
    fecha_primer_dia_mes = primer_dia_mes.strftime("%Y-%m-%d")
    fecha_ultimo_dia_mes = ultimo_dia_mes.strftime("%Y-%m-%d")
    
    # Obtener el primer día del mes anterior
    fecha_un_mes_anterior_dt = (fecha_dt - relativedelta(months=1)).replace(day=1)
    
    # Formatear las fechas en YYYY-MM-DD (no es correcta la comparación en el formato DD-MM-YYYY "15-01-2024" sería mayor que "05-02-2023)
    fecha_un_mes_anterior = fecha_un_mes_anterior_dt.strftime("%Y-%m-%d")
    
    prorrogas = ProrrogaSolicitada.objects.filter(
        asegurado=asegurado,
        fecha_prorroga_solicitada__gte=fecha_primer_dia_mes,
        fecha_prorroga_solicitada__lte=fecha_ultimo_dia_mes,
           
    )
    
    return prorrogas