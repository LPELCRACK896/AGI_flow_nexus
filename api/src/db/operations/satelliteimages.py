from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional, Dict
from datetime import datetime


class SatelliteImagesService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_area_with_products(self, area_id: int) -> Optional[Dict[str, any]]:
        query = text("""
            SELECT a.area_name, ap.product_id, ap.product_name
            FROM areas AS a
            LEFT JOIN areaproducts AS ap ON a.area_id = ap.area_id
            WHERE a.area_id = :area_id
        """)
        result = await self.session.execute(query, {"area_id": area_id})
        rows = result.fetchall()

        if not rows:
            return None

        area_name = rows[0][0]
        products = [{"product_id": row[1], "product_name": row[2]} for row in rows if row[1] is not None]

        return {"area_name": area_name, "products": products}

    async def get_product_name(self, area_id: int, product_id: int) -> Optional[str]:
        query = text("""
            SELECT product_name FROM areaproducts
            WHERE area_id = :area_id AND product_id = :product_id
        """)
        result = await self.session.exec(statement=query, params={"area_id": area_id, "product_id": product_id})
        rows = result.all()

        if not rows:
            return None

        row = rows[0]

        return [{"product_name": row[0]}]

    async def get_etags_in_date_range(self, area_id: int, product_id: int, start_date: datetime, end_date: datetime) -> List[str]:
        query = text("""
            SELECT image_etag FROM satelliteimages
            WHERE area_id = :area_id AND product_id = :product_id
            AND date_time BETWEEN :start_date AND :end_date
            ORDER BY date_time DESC
        """)
        result = await self.session.exec(statement=query, params={"area_id": area_id, "product_id": product_id, "start_date": start_date, "end_date": end_date})

        return [row[0] for row in result.fetchall()]

    async def list_all_areas(self) -> List[dict]:
        query = text("SELECT area_id, area_name FROM areas")
        result = await self.session.exec(statement=query)
        rows = result.all()
        data = [
            {
                "area_id": row[0],
                "area_name": row[1]            }
            for row in rows
        ]

        return data

    async def list_all_products(self) -> List[dict]:
        query = text("""
            SELECT ap.area_id, ap.product_id, ap.product_name, a.area_name
            FROM areaproducts AS ap
            JOIN areas AS a ON ap.area_id = a.area_id
        """)
        result = await self.session.execute(query)
        rows = result.fetchall()

        data = [
            {
                "area_id": row[0],
                "product_id": row[1],
                "product_name": row[2],
                "area_name": row[3]
            }
            for row in rows
        ]

        return data