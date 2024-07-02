from datetime import datetime
import pandas as pd
from .models import CoberturaNominada, CoberturaInnominada

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