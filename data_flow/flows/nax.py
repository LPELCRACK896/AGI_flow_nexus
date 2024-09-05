from utils.routes import nax_check_token, nax_login, nax_get_user
from tasks.connect.redis import get_nax_token, set_nax_token, set_area
from config.config import connections, credentials
from typing import Dict, List, Any, AnyStr
from redis.exceptions import RedisError
from colorama import init, Fore, Style
from pydantic import ValidationError
from prefect import task, flow
from models.Area import Area, AreaUnits
import requests
import redis
from prefect.infrastructure import LocalProcess

init(autoreset=True)
semaphore = LocalProcess(semaphore_limit=2)

class Nax:
    
    def __init__(self, rds: redis.Redis) -> None:
        self.token = None
        self.rds = rds  # Conexión a Redis almacenada

    @flow
    def authentication(self):
        """
        Método principal de autenticación que verifica si existe un token válido o realiza un nuevo login.
        """
        token = get_nax_token(self.rds)
        if token is None:
            print(Fore.RED + f"Error al buscar token en redis")
            print(Fore.CYAN + f"Comienza proceso de login")
            return self.new_login()
        
        valid_token = self.check_token(token)
        if not valid_token:
            print(Fore.RED + f"Token actual invalido: {token}")
            print(Fore.CYAN + f"Comienza proceso de login")
            return self.new_login()
        
        return token

    @flow
    def new_login(self):
        """
        Realiza un nuevo login y actualiza el token en Redis.
        """
        token = self.login(credentials.NAX_USERNAME, credentials.NAX_PASSWORD)
        
        # Verificar si el nuevo token es válido
        valid_token = self.check_token(token)
        if not valid_token:
            print(Fore.RED + f"Token generado inválido: {token}")
            return None

        set_nax_token(self.rds, token)
        return token

    @task
    def login(self, user: str, password: str) -> str:
        """
        Realiza el login y devuelve el token.
        """
        response = nax_login(user, password)

        if response.status_code == 200:
            token = response.content.decode("utf-8").strip('"')
            print(Fore.GREEN + f"Login successful, token stored: {token}")
            return token
        
        print(Fore.RED + f"Login failed with status code: {response.status_code}")
        print(Fore.RED + f"Response: {response.text}")
        raise ValueError("Login failed. Make sure to use proper user and password")

    @task
    def check_token(self, token: str) -> bool:
        """
        Verifica si el token es válido.
        """
        headers = {
            "Authorization": token
        }
        response = nax_check_token(headers=headers)

        if response.status_code == 200:
            return True
        elif response.status_code in [400, 401, 402, 403]:
            data = response.json()
            print(Fore.YELLOW + f"Invalid token. API feedback: {data}")
            return False
        else:
            data = response.json()
            print(Fore.RED + f"Server error. Status code: {response.status_code}, API feedback: {data}")
            raise Exception(f"Server error. Status code: {response.status_code}, API feedback: {data}")
    
    @flow
    def update_areas(self, token):
        raw_areas = self.extract_areas(token)
        processed_areas = self.clean_areas_data(raw_areas)
        futures_set_area = set_area.map([self.rds] * len(processed_areas), processed_areas, task_runner=semaphore)

        failed_set_area = [future.result() is None for future in futures_set_area]

        if any(failed_set_area):
            raise RuntimeError("Set area failed in at least one item.")

        return True
    

    @task(tags=["extract"])
    def extract_areas(self, token):
        headers = {"Authorization": token}
        response = nax_get_user(headers)

        if response.status_code == 200:
            data = response.json()
            if "areas" not in data:
                raise KeyError("Couln't find areas in get user payload")
            return data["areas"]
            

        raise RuntimeError("Unable to get user.")
        
    @task(tags=["transform"])
    def clean_areas_data(self, raw_areas: List[Dict[str, Any]]):
        clean_areas = []
        for r_area in raw_areas:
            try:
                area = Area(**r_area)
                area.units = AreaUnits(**{f"unidad_0{i}": r_area[f"unidad_0{i}"] for i in range(1, 6)})
                clean_areas.append(area)
            except ValidationError as e:
                print(f"Error al procesar el área con id {r_area.get('id')}: {str(e)}")

        return clean_areas
    
