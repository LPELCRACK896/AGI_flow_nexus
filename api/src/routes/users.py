from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from api.src.schemas.users import BodyRegister, BodyLogin
from api.src.db.operations.users import UserService
from api.src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from api.src.functions.encrypt import hash_password, check_password
from api.src.db.models import User
from api.src.functions.token import AuthToken
users_router = APIRouter()

@users_router.post('/register', status_code=HTTPStatus.CREATED)
async def register(
    body: BodyRegister,
    db_session: AsyncSession = Depends(get_session)
    ):

    body.password = hash_password(body.password)

    try:
        new_user = await UserService(db_session).register_user(body)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))

    return {"message": "User registered successfully"}


@users_router.post('/login', status_code=HTTPStatus.ACCEPTED)
async def login(
        body: BodyLogin,
        db_session: AsyncSession = Depends(get_session)
    ):

    found_user = await UserService(db_session).get_user_by_email(body.email)

    if not found_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    user_found: User = found_user[0]
    if not check_password(body.password, user_found.password):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Either email or password is incorrect")

    auth_token = AuthToken(user_id=user_found.id, role_id=user_found.role_id)
    return {
        "message": "Login successful",
        "token": auth_token.encode()
    }