from pydantic import BaseModel

from src.user.schemas import UserRes


class AuthReq(BaseModel):
    name: str
    discord_id: int
    category: str
    career: str


class AuthRes(BaseModel):
    user: UserRes
    access_token: str
    refresh_token: str
