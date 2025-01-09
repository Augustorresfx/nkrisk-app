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
    print(f"Valor recibido en el filtro: {value} (tipo: {type(value)})")  # Para depurar
    try:
        # Si el valor es una cadena, intenta convertirlo a float
        if isinstance(value, str):
            value = value.replace(',', '')  # Elimina comas si las hay
        value = float(value)
        return f"{value:,.2f}"  # Formatea el número
    except (ValueError, TypeError) as e:
        print(f"Error al formatear: {e}")  # Para depurar
        return value  # Retorna el valor original si hay un error

@register.filter
def format_date(value):
    try:
        value = value.strftime("%d/%m/%Y")
        return value
    except (ValueError, TypeError) as e:
        print("Error al formatear fecha: {e}")
        return value