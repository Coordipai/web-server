from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from auth.models import User
from user.service import find_user_by_user_id
from src.config import (
    JWT_SECRET,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_token(data: dict, timedelta: timedelta):
    """
    Create JWT Token util function
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    """
    Create AccessToken
    """
    return create_token(
        {"sub": str(user_id)}, timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    )


def create_refresh_token(user_id: int) -> str:
    """
    Create RefreshToken
    """
    return create_token(
        {"sub": str(user_id)}, timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
    )


# TODO Check token validation
def verify_token(token: str) -> Optional[dict]:
    """
    Verify access token
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
