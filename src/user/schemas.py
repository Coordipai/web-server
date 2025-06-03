from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class UserCategory(str, Enum):
    WEB_FE = "WEB_FE"
    WEB_BE = "WEB_BE"
    AI = "AI"
    MOBILE_APP = "MOBILE_APP"


class UserReq(BaseModel):
    name: str
    discord_id: str
    github_id: int
    github_name: str
    category: UserCategory
    career: str
    profile_img: str


class UserRes(BaseModel):
    id: int
    name: str
    discord_id: str
    github_id: int
    github_name: str
    category: UserCategory
    career: str
    created_at: datetime
    profile_img: str

    model_config = ConfigDict(from_attributes=True)
