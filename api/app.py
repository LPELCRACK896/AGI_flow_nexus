from config.config import Config 
from fastapi import FastAPI

config = Config(env_path=".env", required_fields=["NAX_API_URL", "NAX_USERNAME", "NAX_PASSWORD"])
config.setup()

app = FastAPI()

