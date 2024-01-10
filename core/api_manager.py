import requests
import os
from .models import AccessToken, RefreshToken
from django.utils import timezone
from .api_auth import ApiAuthentication, AuthenticationError

class AuthenticationError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code

class ApiError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code

class ApiManager:
    def get_valid_access_token(self):
        # Verificar si hay un AccessToken válido en la base de datos
        current_time = timezone.now()
        try:
            access_tokens = AccessToken.objects.filter(expiracion__gt=current_time)
            # Verificar si hay al menos un AccessToken válido
            if access_tokens.exists():
                # Obtener el primer AccessToken válido
                return access_tokens.first().token
            else:
                # Intentar refrescar el AccessToken usando el RefreshToken
                if self.refresh_access_token():
                    # Si el refresh fue exitoso, intentar obtener el nuevo AccessToken
                    return self.get_valid_access_token()
                else:
                    return None

        except AccessToken.DoesNotExist:
            # Intentar refrescar el AccessToken usando el RefreshToken
            if self.refresh_access_token():
                # Si el refresh fue exitoso, intentar obtener el nuevo AccessToken
                return self.get_valid_access_token()
            else:
                return None

    def refresh_access_token(self):
        # Intentar refrescar el AccessToken usando el RefreshToken
        try:
            refresh_token = RefreshToken.objects.latest()
            api_auth = ApiAuthentication()  # Instancia de ApiAuthentication
            new_access_token = api_auth.update_token(refresh_token.token)
            return new_access_token
        except RefreshToken.DoesNotExist:
            # Si no hay RefreshToken, intentar autenticarse
            api_auth = ApiAuthentication()  # Instancia de ApiAuthentication
            new_access_token = api_auth.authenticate()
            return new_access_token if new_access_token else None
        except AuthenticationError:
            return False

    def authenticate_api(self):
        # Intentar autenticarse con la API
        try:
            ApiAuthentication.authenticate()
            return True
        except AuthenticationError:
            return False
    
    def get_vehicle_price(self, access_token, codigo_vehiculo):
        # URL del endpoint
        api_url = "https://demo.api.infoauto.com.ar/cars/pub/models/{}/prices/".format(codigo_vehiculo)
        
        # Headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(api_url, headers=headers)

        # Verificar si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            datos_vehiculo = response.json()
            return datos_vehiculo
        else:
            # Manejo de errores
            error_message = f"Error al recibir datos de la API con código de estado: {response.status_code}"
            raise ApiError(error_message, response.status_code)
        
    def get_vehicle_data(self, access_token, codigo_vehiculo):
        # URL del endpoint
        api_url = "https://demo.api.infoauto.com.ar/cars/pub/models/{}/".format(codigo_vehiculo)
        
        # Headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(api_url, headers=headers)
        
        # Verificar si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            datos_vehiculo = response.json()
            return datos_vehiculo
        else:
            # Manejo de errores
            error_message = f"Error al recibir datos de la API con código de estado: {response.status_code}"
            raise ApiError(error_message, response.status_code)
        
    def get_vehicle_features(self, access_token, codigo_vehiculo):
        # URL del endpoint
        api_url = "https://demo.api.infoauto.com.ar/cars/pub/models/{}/features/".format(codigo_vehiculo)
        
        # Headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(api_url, headers=headers)
        
        # Verificar si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            datos_vehiculo = response.json()
            
            # Estructurar los datos en un diccionario
            datos_vehiculo_dict = {(item['category_name'], item['description']): item.get('value', None) for item in datos_vehiculo}


            # Variables para buscar
            categoria_busqueda = "Datos técnicos"
            descripcion_busqueda = "Tipo de vehículo"

            # Buscar directamente en el diccionario
            tipo_vehiculo = datos_vehiculo_dict.get((categoria_busqueda, descripcion_busqueda), None)
            tipo_filtrado = obtener_tipo_vehiculo(tipo_vehiculo)
            return tipo_filtrado
        else:
            # Manejo de errores
            error_message = f"Error al recibir datos de la API con código de estado: {response.status_code}"
            raise ApiError(error_message, response.status_code)
    
def obtener_tipo_vehiculo(tipo_vehiculo):
    # Definir el diccionario de mapeo
    tipo_vehiculo_a_categoria = {
        "SED": "AUTO",
        "CAB": "AUTO",
        "CUP": "AUTO",
        "PKA": "PICK UP CLASE A",
        "FUA": "PICK UP CLASE A",
        "WA4": "PICK UP 4X4",
        "WAG": "AUTO",
        "RUR": "AUTO",
        "PKB": "PICK UP CLASE B",
        "PB4": "PICK UP CLASE B",
        "FUB": "PICK UP CLASE B",
        "JEE": "PICK UP 4X4",
        "MIV": "AUTO",
        "VAN": "AUTO",
        "MBU": "PICK UP CLASE B",
        "LIV": "PICK UP CLASE B",
        "PES": "PICK UP CLASE B",
        "SPE": "PICK UP CLASE B",
    }
    return tipo_vehiculo_a_categoria.get(tipo_vehiculo, "Desconocido")