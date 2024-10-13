from fastapi import FastAPI
from contextlib import asynccontextmanager

from starlette.responses import FileResponse

import projects.agi_api.config.config as cfg
from components.db.postgres.db import init_db
from components.api.routes.models.models_router import model_router
from fastapi.openapi.docs import get_swagger_ui_html

pg_config = cfg.postgres
pg_url = pg_config.DATABASE_URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting...")
    await init_db(pg_url)
    yield
    print("Server is shutting down...")
app = FastAPI(
    title="Agro-intelligence API",
    version="0.0.1",
    docs_url="/docs",
    lifespan=lifespan
)
@app.get("/ping")
async def ping():
    return {"message": "pong"}

general_prefix = "/api/v1"


#Models
app.include_router(router=model_router, prefix="/models", tags=["Models"])



