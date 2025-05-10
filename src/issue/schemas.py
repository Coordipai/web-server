from typing import List

from pydantic import BaseModel

from src.user.schemas import UserRes


class IssueCreateReq(BaseModel):
    repo_fullname: str
    title: str
    body: str
    assignees: List[str]
    priority: str
    iteration: int
    labels: List[str]


class IssueUpdateReq(BaseModel):
    repo_fullname: str
    issue_number: int
    title: str
    body: str
    assignees: List[str]
    priority: str
    iteration: int
    labels: List[str]


class IssueCloseReq(BaseModel):
    repo_fullname: str
    issue_number: int


class IssueRes(BaseModel):
    repo_fullname: str
    issue_number: int
    title: str
    body: str
    assignees: List[UserRes]
    priority: str
    iteration: int
    labels: List[str]
    closed: bool
