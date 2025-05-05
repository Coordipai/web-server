
from fastapi import APIRouter
from src.agent import chain
from sqlalchemy.orm import Session
from fastapi import Depends
from src.config.database import get_db
from src.user import repository as user_repository
from src.agent.schemas import (
    GenerateIssueListRes,
    AssessStatRes,
    AssignedIssueListRes,
    AssignIssueReq
)
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    issue_generate_success,
    assess_success,
    assessment_read_success,
    issue_assign_success
)

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.get(
        "/generate_issues",
        summary="Generate issues",
        response_model=SuccessResponse[GenerateIssueListRes]
        )
async def generate_issues():
    """
    Generate issues using the agent executor.
    """

    executor = chain.CustomAgentExecutor()
    result = await executor.generate_issues()

    return issue_generate_success(result)


@router.get(
        "/assess_stat/{user_id}",
        summary="Assess Stat",
        response_model=SuccessResponse[AssessStatRes]
        )
async def assess_stat(user_id: str, db: Session = Depends(get_db)):
    """
    Assess the competency of a user based on their GitHub activity.
    """
    executor = chain.CustomAgentExecutor()
    result = await executor.assess_competency(user_id, db)

    return assess_success(result)


@router.get(
        "/read_stat/{user_id}",
        summary="Read Stat",
        response_model=SuccessResponse[AssessStatRes]
        )
async def get_stat(user_id: str, db: Session = Depends(get_db)):
    """
    Read stat from the database
    """
    user = user_repository.find_user_by_user_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    return assessment_read_success(AssessStatRes(
        name=user.stat["Name"],
        field=user.stat["Field"],
        experience=user.stat["Experience"],
        evaluation_scores=user.stat["evaluation_scores"],
        implemented_features=user.stat["implemented_features"]
    ))

@router.post(
        "/assign_issues/{project_id}",
        summary="Assign issues to users",
        response_model=SuccessResponse[AssignedIssueListRes]
        )
async def assign_issues(project_id: int, request:AssignIssueReq, db: Session = Depends(get_db)):
    """
    Assign issues to users based on their competency.
    """
    executor = chain.CustomAgentExecutor()
    result = await executor.assign_issue_to_users(db, project_id, request.user_names, request.issues)

    return issue_assign_success(result)
