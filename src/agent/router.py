from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.agent import chain
from src.agent.schemas import (
    AssessStatRes,
    FeedbackReq,
    FeedbackRes,
    GenerateIssueListRes,
    RecommendAssigneeListRes,
    RecommendAssigneeReq,
)
from src.config.database import get_db
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    assess_success,
    feedback_success,
    issue_assign_success,
)

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.get(
    "/generate_issues/{project_id}",
    summary="Generate issues",
    response_model=GenerateIssueListRes,
)
async def generate_issues(project_id: int, db: Session = Depends(get_db)):
    """
    Generate issues using the agent executor.
    """

    executor = chain.CustomAgentExecutor()
    return StreamingResponse(
        executor.generate_issues(project_id, db),
        media_type="application/json",
    )


@router.post(
    "/assess_stat", 
    summary="Assess Stat", 
    response_model=SuccessResponse[AssessStatRes]
)
async def assess_stat(
    request: Request, db: Session = Depends(get_db)
):
    """
    Assess the competency of a user based on their GitHub activity.
    """
    executor = chain.CustomAgentExecutor()
    result = await executor.assess_competency(
        request.state.user_id, db
    )

    return assess_success(result)


@router.post(
    "/recommend_assignees/{project_id}",
    summary="Recommend assignees for issues",
    response_model=SuccessResponse[RecommendAssigneeListRes],
)
async def recommend_assignees(
    project_id: int, recommendAssigneeReq: RecommendAssigneeReq, db: Session = Depends(get_db)
):
    """
    Recommend assignees for issues based on their competency.
    """
    executor = chain.CustomAgentExecutor()
    result = await executor.recommend_assignees(
        db, project_id, recommendAssigneeReq.issues
    )

    return issue_assign_success(result)


@router.get(
    "/feedback",
    summary="Get feedback for issue rescheduling",
    response_model=SuccessResponse[FeedbackRes],
)
async def get_feedback(feedbackReq: FeedbackReq, db: Session = Depends(get_db)):
    """
    Get feedback for issue rescheduling.
    """
    executor = chain.CustomAgentExecutor()
    result = await executor.get_feedback(feedbackReq.project_id, feedbackReq.issue_rescheduling_id, db)

    return feedback_success(result)