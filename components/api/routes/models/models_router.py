from fastapi import FastAPI, APIRouter, Depends
from components.api.routes.models.eagawesome import ea_router

model_router = APIRouter()




model_router.include_router(router=ea_router, prefix="/eagawesome")

