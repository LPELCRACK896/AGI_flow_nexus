from api.src.config import Settings
from sqlalchemy.ext.asyncio import create_async_engine
from api.src.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import text, SQLModel


async_engine = create_async_engine(
    url=settings.PG_DATABASE_URL,
    echo=True
)

async_session_maker = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with async_engine.begin() as conn:
        from api.src.db.models import User, Role
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
