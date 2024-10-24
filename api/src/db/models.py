from sqlalchemy import Integer, String, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    name: str = Field(nullable=False)
    ai_models: bool = Field(default=False, nullable=False)
    satellite_images: bool = Field(default=False, nullable=False)
    meterologic_data: bool = Field(default=False, nullable=False)

    # Relación con usuarios
    users: List["User"] = Relationship(back_populates="role")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    name: str = Field(max_length=250, nullable=False)
    email: str = Field(max_length=250, nullable=False, unique=True)
    password: str = Field(max_length=250, nullable=False)

    role_id: Optional[int] = Field(default=None, foreign_key="roles.id")

    # Relación con roles
    role: Optional[Role] = Relationship(back_populates="users")
