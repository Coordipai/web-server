from typing import List

from pydantic import BaseModel



class IssueReschedulingReq(BaseModel):
    project_id: int
    issue_number: int
    reason: str
    new_iteration: int
    new_assignees: List[str]


class IssueReschedulingRes(BaseModel):
    id: int
    issue_number: int
    reason: str
    old_iteration: int
    new_iteration: int
    old_assignees: List[str]
    new_assignees: List[str]


class IssueReschedulingAiReq(BaseModel):
    project_id: int
    issue_number: int


class IssueReschedulingAiRes(BaseModel):
    ai_feedback: str
    ai_feedback_reason: str
