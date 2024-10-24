from typing import AnyStr
from pydantic import BaseModel

class BodyRegister(BaseModel):
    name: AnyStr
    email: AnyStr
    password: AnyStr
    role_id: int = 1


class BodyLogin(BaseModel):
    email: AnyStr
    password: AnyStr