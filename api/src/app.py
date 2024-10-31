from api.src.routes.satelliteimages import satellite_images_router
from api.src.routes.stations import stations_router, registers_router
from fastapi.middleware.cors import CORSMiddleware
from api.src.routes.users import users_router
from contextlib import asynccontextmanager
from api.src.routes.ml import ml_router
from api.src.db.main import init_db
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting...")
    await init_db()
    yield
    print("Server is shutting down...")


origins = [
    "http://localhost:5173",
    "https://panel.agrointelligence.online",
    "https://arcgismaps.pantaleon.com/"
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
app.include_router(router=stations_router, prefix="/stations", tags=["Stations"])
app.include_router(router=registers_router, prefix="/stations/registers", tags=["Stations Registers"])
app.include_router(router=satellite_images_router, prefix="/satellite_images", tags=["Satellite Images"])