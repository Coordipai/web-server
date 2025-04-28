from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserReq(BaseModel):
    name: str
    discord_id: int
    github_id: int
    github_name: str
    category: str
    career: str


class UserRes(BaseModel):
    name: str
    discord_id: int
    github_id: int
    github_name: str
    category: str
    career: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSearchRes(BaseModel):
    id: int
    name: str
