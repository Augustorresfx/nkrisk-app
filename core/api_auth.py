import requests
import os
from .models import AccessToken, RefreshToken

class AuthenticationError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code

class ApiAuthentication:
    def authenticate(self):
        # Lógica de autenticación con la API externa

        api_url = "https://demo.api.infoauto.com.ar/cars/auth/login"
        
        username = os.environ.get('IA_USER')
        password = os.environ.get('IA_PASSWORD')

        response = requests.post(api_url, auth=(username, password))

        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
            
            AccessToken.objects.create(
                token = access_token
            )
            RefreshToken.objects.create(
                token = refresh_token
            )
            return access_token
        else:
            # Autenticación fallida
            error_message = f"Autenticación fallida con código de estado: {response.status_code}"
            
            raise AuthenticationError(error_message, response.status_code)
    def update_token(self, refresh_token):
        api_url = "https://demo.api.infoauto.com.ar/cars/auth/refresh"

        headers = {
            "Authorization": f"Bearer {refresh_token}"
        }
        
        response = requests.post(api_url, headers=headers)
        
        if response.status_code == 200:
            new_access_token = response.json().get('access_token')
            AccessToken.objects.all().delete()
            AccessToken.objects.create(
                token=new_access_token
            )

            return new_access_token
        else:
            # Renovación fallida
            error_message = f"Renovación del access token fallida con código de estado: {response.status_code}"
            raise AuthenticationError(error_message, response.status_code)
