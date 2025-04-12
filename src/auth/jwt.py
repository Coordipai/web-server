from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from user.service import find_user_by_user_id
import jwt
from datetime import datetime, timedelta
from models import User
from src.auth import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_token(data: dict, timedelta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(datetime.timezone.utc) + timedelta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.ALGORITHM)


def create_access_token(user_id: int) -> str:
    return create_token(
        {"sub": str(user_id)}, timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(user_id: int) -> str:
    return create_token(
        {"sub": str(user_id)}, timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def verify_token(token: str) -> Optional[dict]:
    """
    Verify access token
    """
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user_id = payload.get("sub")
    user = find_user_by_user_id(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
