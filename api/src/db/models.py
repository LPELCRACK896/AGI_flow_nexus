from sqlalchemy import Integer, Column
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

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

    role: Optional[Role] = Relationship(back_populates="users")


class StaticStation(SQLModel, table=True):
    __tablename__ = "staticstations"

    id: Optional[int] = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    station_id: int = Field(sa_column=Column(Integer, unique=True, nullable=False))
    name: Optional[str] = Field(max_length=256)
    latitude: float = Field(nullable=False)
    longitude: float = Field(nullable=False)
    altitude: int = Field(nullable=False)
    stratum: Optional[str] = Field(max_length=256)

    registers: List["StationRegister"] = Relationship(back_populates="station")


class StationRegister(SQLModel, table=True):
    __tablename__ = "stationregisters"

    station_id: int = Field(
        foreign_key="staticstations.station_id", primary_key=True
    )
    date_time: datetime = Field(primary_key=True)
    temperature: Optional[float]
    radiation: Optional[float]
    relative_humidity: Optional[float]
    precipitation: Optional[float]
    wind_speed: Optional[float]
    wetness: Optional[float]
    wind_direction: Optional[float]
    heat_index: Optional[float]

    station: Optional[StaticStation] = Relationship(back_populates="registers")

    class Config:
        indexes = {"ix_station_id_date_time": ("station_id", "date_time DESC")}