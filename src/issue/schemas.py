from typing import List

from pydantic import BaseModel

from src.user.schemas import UserRes


class IssueCreateReq(BaseModel):
    project_id: int
    title: str
    body: str
    assignees: List[str]
    priority: str
    iteration: int
    labels: List[str]


class IssueUpdateReq(BaseModel):
    project_id: int
    issue_number: int
    title: str
    body: str
    assignees: List[str]
    priority: str
    iteration: int
    labels: List[str]


class IssueCloseReq(BaseModel):
    project_id: int
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


class ProjectIssueSummary(BaseModel):
    opened_issues: int
    closed_issues: int
    all_issues: int
