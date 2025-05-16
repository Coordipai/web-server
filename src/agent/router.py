from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.agent import chain
from src.agent.schemas import (
    AssessStatRes,
    AssignedIssueListRes,
    AssignIssueReq,
    GenerateIssueListRes,
)
from src.config.database import get_db
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    assess_success,
    issue_assign_success,
    issue_generate_success,
)

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.get(
    "/generate_issues/{project_id}",
    summary="Generate issues",
    response_model=SuccessResponse[GenerateIssueListRes],
)
async def generate_issues(project_id: int, db: Session = Depends(get_db)):
    """
    Generate issues using the agent executor.
    """

    executor = chain.CustomAgentExecutor()
    result = await executor.generate_issues(project_id, db)

    return issue_generate_success(result)


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
    "/assign_issues/{project_id}",
    summary="Assign issues to users",
    response_model=SuccessResponse[AssignedIssueListRes],
)
async def assign_issues(
    project_id: int, request: AssignIssueReq, db: Session = Depends(get_db)
):
    """
    Assign issues to users based on their competency.
    """
    executor = chain.CustomAgentExecutor()
    result = await executor.assign_issue_to_users(
        db, project_id, request.user_names, request.issues
    )

    return issue_assign_success(result)
