from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AreaUnits(BaseModel):
    unidad_01: Optional[str] = None
    unidad_02: Optional[str] = None
    unidad_03: Optional[str] = None
    unidad_04: Optional[str] = None
    unidad_05: Optional[str] = None

class Area(BaseModel):
    id: int
    name: str = Field(..., alias="nombre")
    id_label: Optional[str] = None
    units: Optional[AreaUnits] = None  # Campo opcional
    last_update: Optional[datetime] = None