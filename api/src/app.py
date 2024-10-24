from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from api.src.routes.ml import ml_router
from api.src.config import settings
from api.src.db.main import init_db
from api.src.routes.users import users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting...")
    await init_db()
    yield
    print("Server is shutting down...")


origins = [
    "http://localhost:5173",
    "https://panel.agrointelligence.online"
]


app = FastAPI(
    title="Agro-intelligence API",
    version="0.0.1",
    docs_url="/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/ping")
async def ping():
    return {"message": "pong"}

general_prefix = "/api/v1"


#Models
app.include_router(router=ml_router, prefix="/ml", tags=["Models"])
app.include_router(router=users_router, prefix="/users", tags=["Users"])


