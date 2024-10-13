from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import text


get_async_engine = lambda database_url: create_async_engine(
    url=database_url,
    echo=True
)

async def init_db(database_url):
    async with AsyncSession(get_async_engine(database_url)) as session:
         statement = text("SELECT 'HELLO';")
         result = await session.exec(statement)
         print(result.all())