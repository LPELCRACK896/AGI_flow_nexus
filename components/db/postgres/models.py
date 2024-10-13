from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4),
    )
    title: str = Field(sa_column=Column(pg.VARCHAR(255)), default="")