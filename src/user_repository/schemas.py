from pydantic import BaseModel


class UserRepositoryReq(BaseModel):
    repo_full_name: str


class UserRepositoryRes(BaseModel):
    repo_full_name: str
