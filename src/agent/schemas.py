from pydantic import BaseModel


class GenerateIssueRes(BaseModel):
    type: str
    name: str
    description: str
    title: str
    labels: list[str]
    sprint: int
    priority: str
    body: list

    @classmethod
    def from_issue(cls, issue: dict) -> "GenerateIssueRes":
        return cls(
            type=issue["type"],
            name=issue["name"],
            description=issue["description"],
            title=issue["title"],
            labels=issue["labels"],
            sprint=issue["sprint"],
            priority="M",
            body=issue["body"]
        )

class GenerateIssueListRes(BaseModel):
    issues: list[GenerateIssueRes]

class AssessStatRes(BaseModel):
    name: str
    field: str
    experience: str
    evaluation_scores: dict
    implemented_features: list[str]

    @classmethod
    def from_stat(cls, stat: dict) -> "AssessStatRes":
        return cls(
            name=stat["Name"],
            field=stat["Field"],
            experience=stat["Experience"],
            evaluation_scores=stat["evaluation_scores"],
            implemented_features=stat["implemented_features"]
        )

class RecommendAssigneeRes(BaseModel):
    issue: str
    assignee: str
    description: list[str]

    @classmethod
    def from_recommendation(cls, recommendation: dict) -> "RecommendAssigneeRes":
        return cls(
            issue=recommendation["issue"],
            assignee=recommendation["assignee"],
            description=recommendation["description"]
        )


class RecommendAssigneeListRes(BaseModel):
    issues: list[RecommendAssigneeRes]

class RecommendAssigneeReq(BaseModel):
    issues: GenerateIssueListRes

class FeedbackReq(BaseModel):
    project_id: int
    issue_rescheduling_id: int
    
class FeedbackRes(BaseModel):
    suggested_assignees: str
    suggested_iteration: int
    reason_for_assignees: str
    reason_for_iteration: str

    @classmethod
    def from_feedback(cls, feedback: dict) -> "FeedbackRes":
        return cls(
            suggested_assignees=feedback["suggestions"]["new_assignee"]["name"],
            suggested_iteration=feedback["suggestions"]["new_sprint"]["sprint"],
            reason_for_assignees=feedback["suggestions"]["new_assignee"]["reason"],
            reason_for_iteration=feedback["suggestions"]["new_sprint"]["reason"]
        )