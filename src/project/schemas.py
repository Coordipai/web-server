from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ProjectReq(BaseModel):
    project_name: str
    repo_name: str
    start_date: datetime
    end_date: datetime
    sprint_unit: int
    discord_chnnel_id: int


class ProjectRes(BaseModel):
    project_id: int
    project_name: str
    repo_name: str
    start_date: datetime
    end_date: datetime
    sprint_unit: int
    discord_channel_id: int

    model_config = ConfigDict(from_attributes=True)
