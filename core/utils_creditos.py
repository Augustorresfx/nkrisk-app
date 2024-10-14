import pandas as pd
from django.db.models import Sum
from .models import CoberturaNominada, CoberturaInnominada
from django.db.models import Q
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import numpy as np

def cargar_datos_nominados(df, asegurado):
    
    for index, row in df.iterrows():
        CoberturaNominada.objects.create(
            asegurado = asegurado,
            id_nacional=row['Id. Nacional'],
            pais=row['País'],
            ciudad=row['Ciudad'],
            cliente=row['Cliente'],
            vigencia_desde=row['Vigencia Desde'],
            vigencia_hasta=row['Vigencia Hasta'],
            moneda=row['Moneda'],
            monto_solicitado=row['Monto Solicitado'],
            monto_aprobado=row['Monto Aprobado'],
            estado=row['Estado'],
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
        fecha_primera_consulta = row['Fecha1era Consulta'].strftime('%Y-%m-%d') if pd.notnull(row['Fecha1era Consulta']) else None
        fecha_ultima_consulta = row['Fecha Última Consulta'].strftime('%Y-%m-%d') if pd.notnull(row['Fecha Última Consulta']) else None
        fecha_hasta_formateada = row['Fecha Hasta'].strftime('%Y-%m-%d') if pd.notnull(row['Fecha Hasta']) else None

        CoberturaInnominada.objects.create(
            asegurado=asegurado,
            id_nacional=row['Id. Nacional'],
            nombre_cliente=row['Cliente'],
            fecha_primer_consulta=fecha_primera_consulta,
            fecha_ultima_consulta=fecha_ultima_consulta,
            estadoActual=row['EstadoActual'],
            codigoAutorizacion=row['CódigoAutorización'],
            fecha_hasta=fecha_hasta_formateada,
            codigoAsegurado=row['CódigoAsegurado'],
        )
        
        
# PRIMER TABLA - Solicitudes de cobertura
def obtener_datos_solicitudes_cobertura(fecha, asegurado):

    # Filtrar coberturas rechazadas y aprobadas
    sol_de_cobertura_rechaz = CoberturaNominada.objects.filter(
        vigencia_desde=fecha,
        estado='RECHAZ',
        asegurado=asegurado,
    )
    sol_de_cobertura_aprob = CoberturaNominada.objects.filter(
        vigencia_desde=fecha,
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
        'sol_de_cobertura_rechaz': sol_de_cobertura_rechaz,
        'sol_de_cobertura_aprob': sol_de_cobertura_aprob,
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

    # Obtener el primer día del mes anterior
    fecha_un_mes_anterior_dt = (fecha_dt - relativedelta(months=1)).replace(day=1)
    
    # Formatear la fecha a "DD/MM/YYYY"
    fecha_un_mes_anterior = fecha_un_mes_anterior_dt.strftime("%d/%m/%Y")

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
        vigencia_desde=fecha,
        estado='ACTIVA',
        asegurado=asegurado,
    ).exclude(id_nacional__in=id_nacional_con_cobertura_anterior).exclude(id_nacional__in=id_nacional_inominados)

    clientes_nuevos_rechaz = CoberturaNominada.objects.filter(
        vigencia_desde=fecha,
        estado='RECHAZ',
        asegurado=asegurado,
    ).exclude(id_nacional__in=id_nacional_con_cobertura_anterior).exclude(id_nacional__in=id_nacional_inominados)

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
        'sol_de_cobertura_rechaz': clientes_nuevos_rechaz,
        'sol_de_cobertura_aprob': clientes_nuevos_aprob,
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
    
# TERCER TABLA - Reestudios
def obtener_datos_reestudios(fecha, asegurado):
    # Convierte la fecha de entrada a un objeto datetime
    fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")

    # Obtener el primer día del mes anterior
    fecha_un_mes_anterior_dt = (fecha_dt - relativedelta(months=1)).replace(day=1)
    
    # Formatear la fecha a "DD/MM/YYYY"
    fecha_un_mes_anterior = fecha_un_mes_anterior_dt.strftime("%d/%m/%Y")
    
    # Obtener el último día del mes anterior de manera segura
    ultimo_dia_un_mes_anterior_dt = fecha_un_mes_anterior_dt.replace(day=calendar.monthrange(fecha_un_mes_anterior_dt.year, fecha_un_mes_anterior_dt.month)[1])
    # Formatear la fecha a "DD/MM/YYYY"
    fecha_ultimo_dia_un_mes_anterior = ultimo_dia_un_mes_anterior_dt.strftime("%d/%m/%Y")

    # Traer los CUITs (id_nacional) de los clientes que tienen coberturas activas (para incluirlos)
    id_nacional_con_cobertura_anterior = CoberturaNominada.objects.filter(
        Q(estado='ACTIVA') | Q(estado='EXPIRA'),
        Q(vigencia_hasta='Indefinida') | Q(vigencia_hasta=fecha_ultimo_dia_un_mes_anterior),
        vigencia_desde__lt=fecha,
        asegurado=asegurado
    ).values_list('id_nacional', flat=True)

    # Filtrar las solicitudes de reestudios aprobadas (ACTIVA) y rechazadas (RECHAZ) cuya id_nacional esté en la lista anterior
    reestudios_aprob = CoberturaNominada.objects.filter(
        vigencia_desde=fecha,
        estado='ACTIVA',
        asegurado=asegurado,
        id_nacional__in=id_nacional_con_cobertura_anterior
    )

    reestudios_rechaz = CoberturaNominada.objects.filter(
        vigencia_desde=fecha,
        estado='RECHAZ',
        asegurado=asegurado,
        id_nacional__in=id_nacional_con_cobertura_anterior
    )

    # Listas para almacenar las coberturas anteriores aprobadas y rechazadas
    coberturas_anteriores_aprob = []
    coberturas_anteriores_rechaz = []

    # Buscar coberturas anteriores para reestudios aprobados
    for reestudio in reestudios_aprob:
        coberturas_anteriores_aprob.extend(
            CoberturaNominada.objects.filter(
                Q(estado='ACTIVA') | Q(estado='EXPIRA'),
                Q(vigencia_hasta='Indefinida') | Q(vigencia_hasta=fecha_ultimo_dia_un_mes_anterior),
                id_nacional=reestudio.id_nacional,
                asegurado=asegurado,
                vigencia_desde__lte=fecha_un_mes_anterior
            )
        )

    # Buscar coberturas anteriores para reestudios rechazados
    for reestudio in reestudios_rechaz:
        coberturas_anteriores_rechaz.extend(
            CoberturaNominada.objects.filter(
                Q(estado='ACTIVA') | Q(estado='EXPIRA'),
                Q(vigencia_hasta='Indefinida') | Q(vigencia_hasta=fecha_ultimo_dia_un_mes_anterior),
                id_nacional=reestudio.id_nacional,
                asegurado=asegurado,
                vigencia_desde__lte=fecha_un_mes_anterior
            )
        )
        
    # Calcular el monto aprobado de las coberturas anteriores
    monto_aprobado_anteriores_aprob = sum(
        cobertura.monto_aprobado for cobertura in coberturas_anteriores_aprob
    )

    monto_aprobado_anteriores_rechaz = sum(
        cobertura.monto_aprobado for cobertura in coberturas_anteriores_rechaz
    )
    monto_aprobado_anteriores_total = monto_aprobado_anteriores_aprob + monto_aprobado_anteriores_rechaz
    
    num_reestudios_rechaz = reestudios_rechaz.count()
    num_reestudios_aprob = reestudios_aprob.count()
    num_total_reestudios = num_reestudios_rechaz + num_reestudios_aprob
    cant_solicitado_rechaz = reestudios_rechaz.aggregate(total=Sum('monto_solicitado'))['total'] or 0
    cant_solicitado_aprob = reestudios_aprob.aggregate(total=Sum('monto_solicitado'))['total'] or 0
    total_solicitado = cant_solicitado_rechaz + cant_solicitado_aprob

    cant_aprobado_aprob = reestudios_aprob.aggregate(total=Sum('monto_aprobado'))['total'] or 0
    
    porcentaje_aprob = 0
    if cant_solicitado_aprob != 0:
        porcentaje_aprob = round((cant_aprobado_aprob / cant_solicitado_aprob) * 100)

    porcentaje_total_aprob = 0
    if total_solicitado != 0:
        porcentaje_total_aprob = round((cant_aprobado_aprob / total_solicitado) * 100)
    
    return {
        'reestudios_rechaz': reestudios_rechaz,
        'reestudios_aprob': reestudios_aprob,
        'num_reestudios_rechaz': num_reestudios_rechaz,
        'num_reestudios_aprob': num_reestudios_aprob,
        'num_total_reestudios': num_total_reestudios,
        'cant_solicitado_rechaz': cant_solicitado_rechaz,
        'cant_solicitado_aprob': cant_solicitado_aprob,
        'total_solicitado': total_solicitado,
        'cant_aprobado_aprob': cant_aprobado_aprob,
        'porcentaje_aprob': porcentaje_aprob,
        'porcentaje_total_aprob': porcentaje_total_aprob,
        'coberturas_anteriores_aprob': coberturas_anteriores_aprob,
        'coberturas_anteriores_rechaz': coberturas_anteriores_rechaz,
        'monto_aprobado_anteriores_aprob': monto_aprobado_anteriores_aprob,
        'monto_aprobado_anteriores_rechaz': monto_aprobado_anteriores_rechaz,
        'monto_aprobado_anteriores_total': monto_aprobado_anteriores_total
    }
    
# CUARTA TABLA - REDUCCIONES / CANCELACIONES
def obtener_datos_reducciones_cancelaciones(fecha, asegurado):
    # Convierte la fecha de entrada a un objeto datetime
    fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")

    # Obtener el primer día del mes anterior
    fecha_un_mes_anterior_dt = (fecha_dt - relativedelta(months=1)).replace(day=1)
    
    # Formatear la fecha a "DD/MM/YYYY"
    fecha_un_mes_anterior = fecha_un_mes_anterior_dt.strftime("%d/%m/%Y")
    
    # Obtener el último día del mes anterior de manera segura
    ultimo_dia_un_mes_anterior_dt = fecha_un_mes_anterior_dt.replace(day=calendar.monthrange(fecha_un_mes_anterior_dt.year, fecha_un_mes_anterior_dt.month)[1])
    # Formatear la fecha a "DD/MM/YYYY"
    fecha_ultimo_dia_un_mes_anterior = ultimo_dia_un_mes_anterior_dt.strftime("%d/%m/%Y")

    