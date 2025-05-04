from pydantic import BaseModel

class GenerateIssueRes(BaseModel):
    issues: list[str]

class AssessStatRes(BaseModel):
    stat: dict[str, str]