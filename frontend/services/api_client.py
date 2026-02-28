import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None
    
    def set_token(self, token):
        self.token = token
    
    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def login(self, email, password):
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        return response
    
    def register(self, email, password, name=""):
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={"email": email, "password": password, "name": name}
        )
        return response
    
    def logout(self):
        response = requests.post(
            f"{self.base_url}/api/auth/logout",
            headers=self._get_headers()
        )
        return response
    
    def get_cilindros(self):
        response = requests.get(
            f"{self.base_url}/api/cilindros",
            headers=self._get_headers()
        )
        return response
    
    def create_cilindro(self, data):
        response = requests.post(
            f"{self.base_url}/api/cilindros",
            json=data,
            headers=self._get_headers()
        )
        return response
    
    def get_cilindro(self, cilindro_id):
        response = requests.get(
            f"{self.base_url}/api/cilindros/{cilindro_id}",
            headers=self._get_headers()
        )
        return response
    
    def update_cilindro(self, cilindro_id, data):
        response = requests.put(
            f"{self.base_url}/api/cilindros/{cilindro_id}",
            json=data,
            headers=self._get_headers()
        )
        return response
    
    def delete_cilindro(self, cilindro_id):
        response = requests.delete(
            f"{self.base_url}/api/cilindros/{cilindro_id}",
            headers=self._get_headers()
        )
        return response
    
    def get_elementos(self):
        response = requests.get(
            f"{self.base_url}/api/elementos",
            headers=self._get_headers()
        )
        return response
    
    def create_elemento(self, data):
        response = requests.post(
            f"{self.base_url}/api/elementos",
            json=data,
            headers=self._get_headers()
        )
        return response
    
    def get_elemento(self, elemento_id):
        response = requests.get(
            f"{self.base_url}/api/elementos/{elemento_id}",
            headers=self._get_headers()
        )
        return response
    
    def update_elemento(self, elemento_id, data):
        response = requests.put(
            f"{self.base_url}/api/elementos/{elemento_id}",
            json=data,
            headers=self._get_headers()
        )
        return response
    
    def delete_elemento(self, elemento_id):
        response = requests.delete(
            f"{self.base_url}/api/elementos/{elemento_id}",
            headers=self._get_headers()
        )
        return response
    
    def get_amostras(self):
        response = requests.get(
            f"{self.base_url}/api/amostras",
            headers=self._get_headers()
        )
        return response
    
    def create_amostra(self, data):
        response = requests.post(
            f"{self.base_url}/api/amostras",
            json=data,
            headers=self._get_headers()
        )
        return response
    
    def get_amostra(self, amostra_id):
        response = requests.get(
            f"{self.base_url}/api/amostras/{amostra_id}",
            headers=self._get_headers()
        )
        return response
    
    def update_amostra(self, amostra_id, data):
        response = requests.put(
            f"{self.base_url}/api/amostras/{amostra_id}",
            json=data,
            headers=self._get_headers()
        )
        return response
    
    def delete_amostra(self, amostra_id):
        response = requests.delete(
            f"{self.base_url}/api/amostras/{amostra_id}",
            headers=self._get_headers()
        )
        return response
    
    def get_tempos(self):
        response = requests.get(
            f"{self.base_url}/api/tempo-chama",
            headers=self._get_headers()
        )
        return response
    
    def create_tempo(self, data):
        response = requests.post(
            f"{self.base_url}/api/tempo-chama",
            json=data,
            headers=self._get_headers()
        )
        return response
    
    def get_tempo(self, tempo_id):
        response = requests.get(
            f"{self.base_url}/api/tempo-chama/{tempo_id}",
            headers=self._get_headers()
        )
        return response
    
    def delete_tempo(self, tempo_id):
        response = requests.delete(
            f"{self.base_url}/api/tempo-chama/{tempo_id}",
            headers=self._get_headers()
        )
        return response


api_client = APIClient()
