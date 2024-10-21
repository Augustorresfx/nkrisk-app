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
        
def consultar_por_divisiones(fecha, asegurado):
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

    # Verificar si alguna cobertura tiene un código de asegurado que no sea nulo, vacío o NaN
    tiene_codigo_asegurado = (
        clientes_nuevos_rechaz.filter(
            Q(codigoAsegurado__isnull=False) & 
            ~Q(codigoAsegurado='') & 
            ~Q(codigoAsegurado=np.nan)
        ).exists() or 
        clientes_nuevos_aprob.filter(
            Q(codigoAsegurado__isnull=False) & 
            ~Q(codigoAsegurado='') & 
            ~Q(codigoAsegurado=np.nan)
        ).exists()
    )
    
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
    fecha_primer_dia_mes = primer_dia_mes.strftime("%d/%m/%Y")
    fecha_ultimo_dia_mes = ultimo_dia_mes.strftime("%d/%m/%Y")

    # Función para obtener los id_nacional y vigencia_desde de las solicitudes "REEMPL" en el rango del mes
    def id_nacional_con_cobertura_reempl(codigo=None):
        # Filtrar las solicitudes con estado "REEMPL" y vigencia_hasta "Indefinida"
        filtro_base = CoberturaNominada.objects.filter(
            estado='REEMPL',
            vigencia_hasta='Indefinida',
            vigencia_desde__gte=fecha_primer_dia_mes,
            vigencia_desde__lte=fecha_ultimo_dia_mes,
            asegurado=asegurado
        )

        # Si se proporciona un código, filtrar por los primeros tres dígitos del codigoAsegurado
        if codigo:
            filtro_base = filtro_base.filter(codigoAsegurado__startswith=codigo)

        # Devolver los id_nacional y las vigencias de las solicitudes "REEMPL"
        return filtro_base.values_list('id_nacional', 'vigencia_desde')

    # Función para filtrar y calcular los datos por código asegurado o sin código
    def filtrar_por_codigo(codigo=None):
        # Obtener los id_nacional y las fechas de vigencia_desde de los "REEMPL"
        id_nacional_y_vigencia_reempl = id_nacional_con_cobertura_reempl(codigo)

        reestudios_aprob = []
        reestudios_rechaz = []

        # Para cada id_nacional y vigencia desde, buscar las solicitudes activas y rechazadas
        for id_nacional, vigencia_desde in id_nacional_y_vigencia_reempl:
            # Buscar la solicitud con estado "ACTIVA" (reestudio aprobado)
            solicitud_aprob = CoberturaNominada.objects.filter(
                id_nacional=id_nacional,
                vigencia_desde=vigencia_desde,
                estado='ACTIVA',
                vigencia_hasta='Indefinida'
            ).first()

            # Buscar la solicitud con estado "RECHAZ" (reestudio rechazado)
            solicitud_rechaz = CoberturaNominada.objects.filter(
                id_nacional=id_nacional,
                vigencia_desde=vigencia_desde,
                estado='RECHAZ',
                vigencia_hasta='Indefinida'
            ).first()

            # Si hay una solicitud aprobada, agregarla a la lista de reestudios aprobados
            if solicitud_aprob:
                reestudios_aprob.append(solicitud_aprob)

            # Si hay una solicitud rechazada, agregarla a la lista de reestudios rechazados
            if solicitud_rechaz:
                reestudios_rechaz.append(solicitud_rechaz)

        # Cálculos y agregados
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
            'porcentaje_total_aprob': porcentaje_total_aprob
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

    # Formatear las fechas a "DD/MM/YYYY"
    fecha_primer_dia_mes = primer_dia_mes.strftime("%d/%m/%Y")
    fecha_ultimo_dia_mes = ultimo_dia_mes.strftime("%d/%m/%Y")

    # Función para obtener cancelaciones con o sin filtro por código
    def obtener_cancelaciones_por_codigo(codigo=None):
        # Filtrar por solicitudes canceladas
        cancelaciones = CoberturaNominada.objects.filter(
            estado='CANCEL',
            vigencia_hasta__gte=fecha_primer_dia_mes,
            vigencia_hasta__lte=fecha_ultimo_dia_mes,
            asegurado=asegurado
        )

        # Si se proporciona un código, filtrar por los primeros tres dígitos del codigoAsegurado
        if codigo:
            cancelaciones = cancelaciones.filter(codigoAsegurado__startswith=codigo)

        # Obtener los datos de interés: cliente, id_nacional y monto_aprobado
        datos_cancelaciones = cancelaciones.values('cliente', 'id_nacional', 'monto_aprobado')

        # Calcular el número de cancelaciones
        num_cancelaciones = cancelaciones.count()

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
    # Convertir la fecha de entrada a un objeto datetime
    fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")

    # Obtener el primer día del mes de entrada
    primer_dia_mes = fecha_dt.replace(day=1)

    # Obtener el último día del mes de entrada de manera segura
    ultimo_dia_mes = primer_dia_mes.replace(day=calendar.monthrange(primer_dia_mes.year, primer_dia_mes.month)[1])

    # Formatear las fechas a "DD/MM/YYYY"
    fecha_primer_dia_mes = primer_dia_mes.strftime("%d/%m/%Y")
    fecha_ultimo_dia_mes = ultimo_dia_mes.strftime("%d/%m/%Y")

    # Función para obtener reducciones con o sin filtro por código
    def obtener_reducciones_por_codigo(codigo=None):
        # Filtrar solicitudes de cobertura con estado REEMPL
        solicitudes_reempl = CoberturaNominada.objects.filter(
            estado='REEMPL',
            vigencia_desde__gte=fecha_primer_dia_mes,
            vigencia_desde__lte=fecha_ultimo_dia_mes,
            vigencia_hasta='Indefinida',
            asegurado=asegurado
        )

        # Si se proporciona un código, filtrar por los primeros tres dígitos del codigoAsegurado
        if codigo:
            solicitudes_reempl = solicitudes_reempl.filter(codigoAsegurado__startswith=codigo)

        # Lista para almacenar reducciones
        reducciones = []

        # Iterar sobre las solicitudes REEMPL para encontrar las reducciones
        for solicitud_reempl in solicitudes_reempl:
            # Buscar la solicitud ACTIVA o RECHAZ que la reemplazó
            solicitudes_activas = CoberturaNominada.objects.filter(
                estado__in=['ACTIVA', 'RECHAZ'],
                vigencia_desde=solicitud_reempl.vigencia_desde,
                vigencia_hasta='Indefinida',
                asegurado=asegurado,
                codigoAsegurado=solicitud_reempl.codigoAsegurado
            )

            # Comparar el monto aprobado de la solicitud ACTIVA/RECHAZ con la solicitud REEMPL
            for solicitud_activa in solicitudes_activas:
                if solicitud_activa.monto_aprobado < solicitud_reempl.monto_aprobado:
                    # Si es una reducción, agregarla a la lista
                    reducciones.append({
                        'cliente': solicitud_activa.cliente,
                        'id_nacional': solicitud_activa.id_nacional,
                        'monto_aprobado': solicitud_activa.monto_aprobado,
                        'diferencia': solicitud_reempl.monto_aprobado - solicitud_activa.monto_aprobado
                    })

        # Calcular el número de reducciones (un simple count)
        num_reducciones = len(reducciones)

        # Calcular el total del monto aprobado en reducciones
        total_monto_aprobado = sum(reduccion['monto_aprobado'] for reduccion in reducciones)

        return {
            'datos_reducciones': reducciones,
            'num_reducciones': num_reducciones,
            'total_monto_aprobado': total_monto_aprobado
        }

    # Verificar si alguna solicitud de cobertura tiene codigoAsegurado para este asegurado
    existe_codigo_asegurado = CoberturaNominada.objects.filter(
        asegurado=asegurado,
        codigoAsegurado__isnull=False
    ).exists()

    if existe_codigo_asegurado:
        # Reducciones para "Envases" (código 100)
        reducciones_envases = obtener_reducciones_por_codigo('100')

        # Reducciones para "Cartulinas" (código 200)
        reducciones_cartulinas = obtener_reducciones_por_codigo('200')
    else:
        # Si no hay codigoAsegurado, no hacer separaciones por código
        reducciones_envases = None
        reducciones_cartulinas = None

    # Reducciones sin separación por códigoAsegurado
    reducciones_sin_separacion = obtener_reducciones_por_codigo()

    # Combinar todas las reducciones en un solo diccionario para el retorno
    return {
        'cliente': [red['cliente'] for red in reducciones_sin_separacion['datos_reducciones']],
        'id_nacional': [red['id_nacional'] for red in reducciones_sin_separacion['datos_reducciones']],
        'num_reducciones': reducciones_sin_separacion['num_reducciones'],
        'total_monto_aprobado': reducciones_sin_separacion['total_monto_aprobado'],
        'reducciones_envases': reducciones_envases,
        'reducciones_cartulinas': reducciones_cartulinas
    }
