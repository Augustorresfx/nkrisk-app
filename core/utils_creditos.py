import pandas as pd
from django.db.models import Sum
from .models import CoberturaNominada, CoberturaInnominada
from django.db.models import Q
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
            asegurado = asegurado,
            id_nacional=row['Id. Nacional'],
            nombre_cliente=row['Cliente'],
            fecha_primer_consulta=row['Fecha1era Consulta'],
            fecha_ultima_consulta=row['Fecha Última Consulta'],
            estadoActual=row['EstadoActual'],
            codigoAutorizacion=row['CódigoAutorización'],
            fecha_hasta=row['Fecha Hasta'],
            codigoAsegurado=row['CódigoAsegurado'],
        )
        
        
# PRIMER TABLA - Solicitudes de cobertura
def obtener_datos_solicitudes_cobertura(fecha, asegurado):
    
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
    num_cobertura_rechaz = sol_de_cobertura_rechaz.count()
    num_cobertura_aprob = sol_de_cobertura_aprob.count()
    num_total_cobertura = num_cobertura_rechaz + num_cobertura_aprob
    cant_solicitado_rechaz = sol_de_cobertura_rechaz.aggregate(total=Sum('monto_solicitado'))['total'] or 0
    cant_solicitado_aprob = sol_de_cobertura_aprob.aggregate(total=Sum('monto_solicitado'))['total'] or 0
    total_solicitado = cant_solicitado_rechaz + cant_solicitado_aprob

    cant_aprobado_aprob = sol_de_cobertura_aprob.aggregate(total=Sum('monto_aprobado'))['total'] or 0
    
    
    porcentaje_aprob = 0
    if cant_solicitado_aprob != 0:
        porcentaje_aprob = round((cant_aprobado_aprob / cant_solicitado_aprob) * 100)

    porcentaje_total_aprob = 0
    if total_solicitado != 0:
        porcentaje_total_aprob = round((cant_aprobado_aprob / total_solicitado) * 100)

    
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

    print(clientes_nuevos_aprob)
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
