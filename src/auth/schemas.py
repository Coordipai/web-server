from typing import List
from pydantic import BaseModel

class GitHubUser(BaseModel):
    login: str
    id: int
    html_url: str
    notification_email: str

class RepoInfo(BaseModel):
    name: str
    private: bool
    url: str
    description: str | None

class GitHubAuthResponse(BaseModel):
    user: GitHubUser
    repositories: List[RepoInfo]
    