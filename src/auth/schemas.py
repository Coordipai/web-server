from pydantic import BaseModel

from src.user.schemas import UserCategory, UserRes


class AuthReq(BaseModel):
    name: str
    discord_id: str
    category: UserCategory
    career: str


class AuthRes(BaseModel):
    user: UserRes
    access_token: str
    refresh_token: str


class RefreshReq(BaseModel):
    refresh_token: str
