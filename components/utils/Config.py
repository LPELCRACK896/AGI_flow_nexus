from dotenv import dotenv_values
from typing import Tuple, List
import os


class Config:
    def __init__(self, path, required_fields=[]) -> None:
        self.path = path
        self.__config = None
        self.required_fields = required_fields

    def set_config(self, config):
        self.__config = config

    def get_config(self):
        return self.__config

    def setup(self):
        config = self.__get_envs()
        match_required_fields, missing_fields = self.contains_required_fields(config)
        if match_required_fields:
            self.__config = config
            return

        raise ValueError(f"Could not find required fields: {','.join(missing_fields)} in given enf file ({self.path})")

    def __get_envs(self):
        if os.path.exists(self.path):
            return dotenv_values(self.path)
        raise FileNotFoundError(
            f"The environment file at {self.path} was not found. TIP: your current path is {os.getcwd()}")

    def contains_required_fields(self, config) -> Tuple[bool, List[str]]:
        given_fields = set(config.keys())
        remaining_fields = [field for field in self.required_fields if field not in given_fields]
        return not remaining_fields, remaining_fields

    def __getattr__(self, name: str):
        """Permite acceder a las variables de entorno como si fueran atributos de la clase"""
        if name in self.__dict__:
            return self.__dict__[name]

        if self.__config is None:
            raise ValueError("Configuration is not set up. Call setup() first.")

        if name in self.__config:
            if name.endswith("_PORT"):
                return int(self.__config[name])
            return self.__config[name]

        raise AttributeError(f"'Config' object has no attribute '{name}'")


