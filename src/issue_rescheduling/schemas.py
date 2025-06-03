from enum import Enum
from typing import List

from pydantic import BaseModel

from src.issue.schemas import IssueRes
from src.issue_rescheduling.models import IssueRescheduling
from src.user.models import User


class IssueReschedulingType(str, Enum):
    APPROVED = ("APPROVED",)
    REJECTED = ("REJECTED",)


class IssueReschedulingReq(BaseModel):
    issue_number: int
    reason: str
    new_iteration: int
    new_assignees: List[str]


class IssueReschedulingRes(BaseModel):
    id: int
    issue_number: int
    requester: str
    reason: str
    old_iteration: int
    new_iteration: int
    old_assignees: List[str]
    new_assignees: List[str]

    @classmethod
    def from_issue(
        cls,
        issue_rescheduling: IssueRescheduling,
        request: User,
        issue: IssueRes,
    ) -> "IssueReschedulingRes":
        return cls(
            id=issue_rescheduling.id,
            issue_number=issue_rescheduling.issue_number,
            requester=request.github_name,
            reason=issue_rescheduling.reason,
            old_iteration=issue.iteration,
            new_iteration=issue_rescheduling.new_iteration,
            old_assignees=[assignee.github_name for assignee in issue.assignees],
            new_assignees=issue_rescheduling.new_assignees,
        )


class IssueReschedulingAiReq(BaseModel):
    project_id: int
    issue_number: int


class IssueReschedulingAiRes(BaseModel):
    ai_feedback: str
    ai_feedback_reason: str
