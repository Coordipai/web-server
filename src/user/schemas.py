from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserReq(BaseModel):
    name: str
    discord_id: int
    github_id: int
    github_name: str
    category: str
    career: str
    profile_img: str


class UserRes(BaseModel):
    id: int
    name: str
    discord_id: int
    github_id: int
    github_name: str
    category: str
    career: str
    created_at: datetime
    profile_img: str

    model_config = ConfigDict(from_attributes=True)
