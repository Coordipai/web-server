from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: Optional[str] = None
    discord_id: int
    github_id: int
    github_name: str
    category: str
    career: str

    model_config = {"from_attributes": True}


class AuthUser(BaseModel):
    user: Optional[User] = None
    access_token: str
    refresh_token: str
