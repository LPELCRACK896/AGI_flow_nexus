from components.requests.nax_requests import (
    nax_check_token, nax_login, nax_get_user, nax_get_values, nax_get_multiple_tiff_images
)
from colorama import init, Fore, Style
from components.prefect.tasks.redis_tasks import get_nax_token, set_nax_token, set_area
from projects.nax_etl.config.config import credentials
from typing import Dict, List, Any
from components.prefect.models.Area import Area, AreaUnits
from pydantic import ValidationError
from prefect import task, flow
import datetime
import redis
import json
import os

init(autoreset=True)

class NaxFlows:
    def __init__(self, rds: redis.Redis):
        self.token = None
        self.rds = rds  # Redis connection storage

    @flow
    def authentication(self):
        """
        Main authentication method that checks if a valid token exists or performs a new login.
        """
        token = get_nax_token(self.rds)
        if token is None:
            print(Fore.RED + "Error retrieving token from Redis")
            print(Fore.CYAN + "Starting login process")
            return self.new_login()

        valid_token = self.check_token(token)
        if not valid_token:
            print(Fore.RED + f"Invalid current token: {token}")
            print(Fore.CYAN + "Starting login process")
            return self.new_login()

        return token

    @flow
    def new_login(self):
        """
        Performs a new login and updates the token in Redis.
        """
        token = self.login(credentials.NAX_USERNAME, credentials.NAX_PASSWORD)

        # Verify if the new token is valid
        valid_token = self.check_token(token)
        if not valid_token:
            print(Fore.RED + f"Generated token is invalid: {token}")
            return None

        set_nax_token(self.rds, token)
        return token

    @task
    def login(self, user: str, password: str) -> str:
        """
        Performs the login and returns the token.
        """
        response = nax_login(user, password)

        if response.status_code == 200:
            token = response.content.decode("utf-8").strip('"')
            print(Fore.GREEN + f"Login successful, token stored: {token}")
            return token

        print(Fore.RED + f"Login failed with status code: {response.status_code}")
        print(Fore.RED + f"Response: {response.text}")
        raise ValueError("Login failed. Ensure proper user and password")

    @task
    def check_token(self, token: str) -> bool:
        """
        Verifies if the token is valid.
        """
        response = nax_check_token(token=token)

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
        futures_set_area = set_area.map([self.rds] * len(processed_areas), processed_areas)

        failed_set_area = [future.result() is None for future in futures_set_area]

        if any(failed_set_area):
            raise RuntimeError("Set area failed for at least one item.")

        return True

    @flow
    def upload_values(self, token, area_id, date: datetime.datetime):
        data = self.fetch_values(token=token, area_id=area_id, date=date)
        self.save_json(json_data=data, filename=f"data_{area_id}_{date.strftime('%Y-%m-%d')}.json")

    @flow
    def etl_tiff_images(self, token: str, area_id: int, product_name: str, start_date: datetime.datetime,
                        end_date: datetime.datetime):
        json_images_drive_url = self.fetch_images_drive_url(token, area_id, product_name, start_date, end_date)

    @task
    def fetch_images_drive_url(self, token: str, area_id: int, product_name: str, start_date: datetime.datetime,
                               end_date: datetime.datetime):
        response = nax_get_multiple_tiff_images(token, area_id, product_name, start_date, end_date)

        if response.status_code == 200:
            data = response.json()
            if "download_link" in data:
                return data
            raise KeyError(f"Couldn't find download_link in the response: {data}")

        raise ValueError(f"Error encountered while requesting drive URL. Feedback: {response.json()}")

    @task
    def fetch_values(self, token, area_id, date):
        response = nax_get_values(token=token, area_id=area_id, start_date=date, end_date=date)
        return response.json()

    @task
    def save_json(self, json_data: dict, path="./notebooks/data", filename="data.json"):
        if not os.path.exists(path):
            os.makedirs(path)
        file_path = os.path.join(path, filename)

        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f"Data saved at {file_path}")

    @task(tags=["extract"])
    def extract_areas(self, token):
        response = nax_get_user(token)

        if response.status_code == 200:
            data = response.json()
            if "areas" not in data:
                raise KeyError("Couldn't find 'areas' in the user payload")
            return data["areas"]

        raise RuntimeError("Unable to retrieve user data.")

    @task(tags=["transform"])
    def clean_areas_data(self, raw_areas: List[Dict[str, Any]]):
        clean_areas = []
        for r_area in raw_areas:
            try:
                area = Area(**r_area)
                area.units = AreaUnits(**{f"unidad_0{i}": r_area[f"unidad_0{i}"] for i in range(1, 6)})
                clean_areas.append(area)
            except ValidationError as e:
                print(f"Error processing area with ID {r_area.get('id')}: {str(e)}")

        return clean_areas
