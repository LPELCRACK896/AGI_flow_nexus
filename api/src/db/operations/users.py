from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import insert, select
from api.src.db.models import User
from api.src.schemas.users import BodyRegister

class UserService:
    def __init__(self, session):
        self.session = session
        print(session)

    async def register_user(self, user: BodyRegister):
        new_user = User(**user.model_dump())

        self.session.add(new_user)
        await self.session.commit()

        return new_user


    async def get_user_by_email(self, email):
        statement = select(User).where(User.email == email)
        result = await self.session.exec(statement)

        return result.first()