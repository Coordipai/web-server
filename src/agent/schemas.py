from pydantic import BaseModel


class GenerateIssueRes(BaseModel):
    type: str
    name: str
    description: str
    title: str
    labels: list[str]
    body: list

class GenerateIssueListRes(BaseModel):
    issues: list[GenerateIssueRes]

class AssessStatReq(BaseModel):
    user_id: str
    selected_repos: list[str]

class AssessStatRes(BaseModel):
    name: str
    field: str
    experience: str
    evaluation_scores: dict
    implemented_features: list[str]

class AssignedIssueRes(BaseModel):
    issue: str
    assignee: str
    description: list[str]

class AssignedIssueListRes(BaseModel):
    issues: list[AssignedIssueRes]

class AssignIssueReq(BaseModel):
    user_names: list[str]
    issues: GenerateIssueListRes