from api.src.db.operations.stationregisters import StationRegisterService
from api.src.db.operations.staticstations import StaticStationService
from api.src.db.models import StaticStation, StationRegister
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import APIRouter,Depends, HTTPException
from api.src.db.main import get_session
from datetime import datetime
from http import HTTPStatus
from typing import List


stations_router = APIRouter()


@stations_router.get("/")
async def get_stations(db_session: AsyncSession = Depends(get_session)):
    """
    GET all stations data.
    :param db_session: FastAPI dependency injection (handled by server).
    :return:
    """
    stations_data: List[StaticStation] = await StaticStationService(db_session).get_all_stations()

    if not stations_data:
        raise HTTPException(status_code=404, detail="No stations found")
    return {"success": True, "data": stations_data}

@stations_router.get("/{station_id}")
async def get_station(
        station_id: int, db_session: AsyncSession = Depends(get_session)
):
    """
    GET station's details given the station id.
    :param station_id:
    :param db_session: FastAPI dependency injection (handled by server).
    :return:
    """
    found_station = await StaticStationService(db_session).get_station_by_station_id(station_id)
    if not found_station:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return {"success": True, "data": found_station}

registers_router = APIRouter()

@registers_router.get("/", response_model=List[StationRegister], status_code=HTTPStatus.OK)
async def get_registers_in_range(
        station_id: int,
        start_date: datetime ,
        end_date: datetime ,
        db_session: AsyncSession = Depends(get_session)
):
    """
    GET all registers of a given station_id between start_date and end_date
    :param station_id:
    :param start_date:
    :param end_date:
    :param db_session:
    :return:
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be earlier than end_date"
        )

    service = StationRegisterService(db_session)
    registers = await service.get_registers_in_range(station_id, start_date, end_date)

    if not registers:
        raise HTTPException(status_code=404, detail="No registers found")

    return { "success": True, "data": registers }


@registers_router.get("/daily_avg/", response_model=List[dict])
async def get_daily_avg_temp_and_precip(
    station_id: int,
    start_date: datetime,
    end_date: datetime,
    db_session: AsyncSession = Depends(get_session)
):
    """
    GET daily average temperature and precipitation of a given station_id
    :param station_id:
    :param start_date:
    :param end_date:
    :param db_session:
    :return:
    """
    service = StationRegisterService(db_session)
    result = await service.get_daily_avg_temp_and_precip(station_id, start_date, end_date)
    return result

@registers_router.get("/hourly_avg/", response_model=List[dict])
async def get_hourly_avg_temp_last_day(db_session: AsyncSession = Depends(get_session)):
    """
    GET average temperature of the last 24 hours for each station.
    :param db_session:
    :return:
    """
    service = StationRegisterService(db_session)
    result = await service.get_hourly_avg_temp_last_day()
    return result

@registers_router.get("/daily_extremes/", response_model=List[dict])
async def get_daily_extremes(
    station_id: int,
    start_date: datetime,
    end_date: datetime,
    db_session: AsyncSession = Depends(get_session)
):
    """
    GET daily extremes temperatures, wind speed and radiation of a given station.
    :param station_id:
    :param start_date:
    :param end_date:
    :param db_session:
    :return:
    """
    service = StationRegisterService(db_session)
    result = await service.get_daily_extremes(station_id, start_date, end_date)
    return result

@registers_router.get("/weekly_precip/", response_model=List[dict])
async def get_weekly_precipitation(
    start_date: datetime,
    end_date: datetime,
    db_session: AsyncSession = Depends(get_session)
):
    """
    GET accumulative precipitation groped by weeks.
    :param start_date:
    :param end_date:
    :param db_session:
    :return:
    """
    service = StationRegisterService(db_session)
    result = await service.get_weekly_precipitation(start_date, end_date)
    return result

@registers_router.get("/last_registers/", response_model=List[dict])
async def get_last_registers(db_session: AsyncSession = Depends(get_session)):
    """
    GET last registers data available for each station.
    :param db_session:
    :return:
    """
    service = StationRegisterService(db_session)
    result = await service.get_last_registers()
    return result
