from pydantic import BaseModel

class GenerateIssueRes(BaseModel):
    type: str
    name: str
    description: str
    title: str
    lablels: list[str]
    priority: str
    body: dict[str, str]

class GenerateIssueListRes(BaseModel):
    issues: list[GenerateIssueRes]

class AssessStatRes(BaseModel):
    name: str
    field: str
    experience: str
    evaluatino_scores: dict[str, float]
    implemented_features: list[str]