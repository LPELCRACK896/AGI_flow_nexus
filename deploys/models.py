from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Product(BaseModel):
    id: int
    name:str
    title:str


class Area(BaseModel):
    id: int
    name: str
    title: str
    products: List[Product] = []


    def __repr__(self):
        return f"{self.name}({self.id})"
