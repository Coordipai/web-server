from pydantic import BaseModel


class UserRepositoryReq(BaseModel):
    repo_fullname: str


class UserRepositoryRes(BaseModel):
    repo_fullname: str
