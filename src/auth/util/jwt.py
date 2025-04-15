from typing import Optional
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from datetime import datetime, timedelta, timezone
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


def create_access_token(id: int) -> str:
    """
    Create AccessToken
    """
    return create_token(
        {"sub": str(id)}, timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    )


def create_refresh_token(id: int) -> str:
    """
    Create RefreshToken
    """
    return create_token(
        {"sub": str(id)}, timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
    )


def parse_token(token: str) -> Optional[dict]:
    """
    Verify access token
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
