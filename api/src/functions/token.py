from fastapi import  HTTPException
from jwt import PyJWTError, encode, decode, ExpiredSignatureError
from typing import AnyStr, Union
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from typing import AnyStr
from datetime import datetime, timedelta
from api.src.config import settings

algorithm: AnyStr = settings.JWT_ALGORITHM
secret = settings.JWT_SECRET_KEY

class AuthToken(BaseModel):
    user_id: int
    role_id: int
    expires_in: int = Field(default=86400)  # 1 día en segundos
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def create(user_id: str, role_id: str, expires_in: int = 86400) -> dict:
        """Genera un token JWT con los datos del usuario."""
        created_at = datetime.utcnow()
        expire_at = created_at + timedelta(seconds=expires_in)
        payload = {
            "user_id": user_id,
            "role_id": role_id,
            "exp": expire_at,
            "iat": created_at
        }
        return payload

    def encode(self):
        return encode(self.model_dump(exclude={"created_at"}), secret, algorithm=algorithm)


def verify_token(token: str) -> Union[AuthToken, HTTPException]:
    try:
        payload = decode(token, secret, algorithms=[algorithm])

        auth_token = AuthToken(**payload)

        expiration_time = auth_token.created_at + timedelta(seconds=auth_token.expires_in)
        current_time = datetime.now(timezone.utc)

        if current_time > expiration_time:
            raise HTTPException(status_code=401, detail="Token has expired")

        return auth_token

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
