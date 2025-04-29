from pydantic import BaseModel, ConfigDict
from datetime import datetime

from src.user.schemas import UserRes


class ProjectReq(BaseModel):
    name: str
    repo_name: str
    start_date: datetime
    end_date: datetime
    sprint_unit: int
    discord_chnnel_id: int


class ProjectRes(BaseModel):
    id: int
    name: str
    owner: UserRes
    repo_name: str
    start_date: datetime
    end_date: datetime
    sprint_unit: int
    discord_channel_id: int

    model_config = ConfigDict(from_attributes=True)
