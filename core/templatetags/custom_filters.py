from django import template
import datetime

register = template.Library()

@register.filter
def get_years_to_current(value):
    return range(2020, datetime.datetime.now().year + 1)

@register.filter
def get_months(value):
    return range(1, 13)

@register.filter
def get_month_name(value):
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    try:
        return months[int(value) - 1]
    except (ValueError, IndexError):
        return value  # O manejar el error de alguna otra forma

@register.filter
def format_number(value):
    """Formatea un número para usar punto como separador de miles y coma para decimales."""
    if value is None:
        return ''
    
    # Formatear el número
    formatted_value = f'{value:,.2f}'  # Usa 2 decimales para que haya una coma
    # Cambiar la coma a punto y el punto a coma
    formatted_value = formatted_value.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    return formatted_value