from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from api.src.db.models import StaticStation
from typing import List, Optional

class StaticStationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_stations(self) -> List[StaticStation]:
        statement = select(StaticStation)
        result = await self.session.exec(statement)
        return result.scalars().all()

    async def get_station_by_station_id(self, station_id: int) -> Optional[StaticStation]:
        statement = select(StaticStation).where(StaticStation.station_id == station_id)
        result = await self.session.exec(statement)
        return result.scalars().first()
