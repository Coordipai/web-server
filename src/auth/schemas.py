from typing import Optional
from pydantic import BaseModel, Field


class GitHubUser(BaseModel):
    login: str
    id: int
    html_url: str
    email: Optional[str] = None


class RepoInfo(BaseModel):
    name: str
    private: bool
    url: str
    description: str | None


class User(BaseModel):
    name: str
    email: Optional[str] = None
    discord_id: int
    github_id: int
    github_name: str
    category: str
    career: str

    model_config = {"from_attributes": True}
