from sqlalchemy import select, func, desc, and_, text
from sqlmodel.ext.asyncio.session import AsyncSession
from api.src.db.models import StationRegister
from typing import List, Optional, Dict
from datetime import datetime, date

class StationRegisterService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_registers_in_range(self, station_id: int, start_date: datetime, end_date: datetime) -> List[StationRegister]:
        """
        Obtener todos los registros de una estación entre dos fechas.
        """
        statement = (
            select(StationRegister)
            .where(
                and_(
                    StationRegister.station_id == station_id,
                    StationRegister.date_time.between(start_date, end_date),
                )
            )
            .order_by(StationRegister.date_time.asc())
        )
        result = await self.session.exec(statement)
        return result.scalars().all()

    async def get_daily_avg_temp_and_precip(self, station_id: int, start_date: datetime, end_date: datetime):
        """
        Obtener el promedio de temperatura y acumulación de precipitación diaria.
        """
        statement = text(f"""
            SELECT time_bucket('1 day', date_time) AS day,
                   station_id,
                   AVG(temperature) AS avg_temp,
                   SUM(precipitation) AS total_precip
            FROM stationregisters
            WHERE station_id = :station_id
              AND date_time BETWEEN :start_date AND :end_date
            GROUP BY day, station_id
            ORDER BY day DESC
        """)
        result = await self.session.exec(statement=statement, params={"station_id": station_id, "start_date": start_date, "end_date": end_date})
        rows = result.all()
        data = [
            {
                "day": row[0],
                "station_id": row[1],
                "avg_temp": row[2],
                "total_precip": row[3]
            }
            for row in rows
        ]
        return data

    async def get_hourly_avg_temp_last_day(self):
        """
        Obtener el promedio de temperatura por hora en las últimas 24 horas.
        """
        statement = text("""
            SELECT time_bucket('1 hour', date_time) AS bucket,
                   station_id,
                   AVG(temperature) AS avg_temp
            FROM stationregisters
            WHERE date_time >= NOW() - INTERVAL '1 day'
            GROUP BY bucket, station_id
            ORDER BY bucket DESC
        """)
        result = await self.session.exec(statement=statement)
        rows = result.all()
        data = [
            {
                "bucket": row[0],
                "station_id": row[1],
                "avg_temp": row[2]
            }
            for row in rows
        ]

        return data

    async def get_daily_extremes(self, station_id: int, start_date: datetime, end_date: datetime):
        """
        Obtener los valores máximos y mínimos diarios para temperatura, velocidad del viento y radiación.
        """
        statement = text(f"""
            SELECT time_bucket('1 day', date_time) AS day,
                   station_id,
                   MAX(temperature) AS max_temp,
                   MIN(temperature) AS min_temp,
                   MAX(wind_speed) AS max_wind_speed,
                   MIN(radiation) AS min_radiation
            FROM stationregisters
            WHERE station_id = :station_id
              AND date_time BETWEEN :start_date AND :end_date
            GROUP BY day, station_id
            ORDER BY day DESC
        """)
        result = await self.session.exec(statement=statement, params={"station_id": station_id, "start_date": start_date, "end_date": end_date})
        rows = result.all()
        data = [
            {
                "day": row[0],
                "station_id": row[1],
                "max_temp": row[2],
                "min_temp": row[3],
                "max_wind_speed": row[4],
                "min_radiation": row[5]
            }
            for row in rows
        ]


        return data

    async def get_weekly_precipitation(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Obtener la acumulación semanal de precipitación.
        """
        statement = text("""
            SELECT time_bucket('1 week', date_time) AS week,
                   station_id,
                   SUM(precipitation) AS total_precip
            FROM stationregisters
            WHERE date_time BETWEEN :start_date AND :end_date
            GROUP BY week, station_id
            ORDER BY week DESC
        """)
        result = await self.session.exec(
            statement=statement,
            params={"start_date": start_date, "end_date": end_date}
        )

        rows = result.all()

        data = [
            {
                "week": row[0],
                "station_id": row[1],
                "total_precip": row[2]
            }
            for row in rows
        ]

        return data

    async def get_last_registers(self):
        """
        Obtener el último registro disponible para cada estación.
        """
        statement = text("""
            SELECT station_id, temperature AS last_temp, wind_speed AS last_wind_speed, precipitation AS last_precip, date_time
            FROM stationregisters sr
            WHERE date_time = (
                SELECT MAX(date_time)
                FROM stationregisters
                WHERE station_id = sr.station_id
            )
        """)
        result = await self.session.exec(statement=statement)
        rows = result.all()

        data = [
            {
                "station_id": row[0],
                "last_temp": row[1],
                "last_wind_speed": row[2],
                "last_precip": row[3],
                "date_time": row[4]
            }
            for row in rows
        ]

        return data