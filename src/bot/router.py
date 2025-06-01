from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from src.bot.util import send_daily_request
from src.config.database import get_db
from src.issue import service as issue_service
from src.issue.schemas import IssueRes
from src.issue_rescheduling import service as issue_rescheduling_service
from src.issue_rescheduling.schemas import IssueReschedulingReq, IssueReschedulingRes
from src.project import repository as project_repository
from src.project import service as project_service
from src.project.schemas import ProjectRes
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    issue_read_success,
    issue_rescheduling_create_success,
    project_read_success,
)
from src.user import repository as user_repository

router = APIRouter(prefix="/bot", tags=["Bot"])


@router.get(
    "/project",
    summary="Get existing project",
    response_model=SuccessResponse[ProjectRes],
)
def get_project(
    discord_channel_id: str = Header(..., description="Discord Channel ID"),
    discord_user_id: str = Header(..., description="Discord User ID"),
    db: Session = Depends(get_db),
):
    user = user_repository.find_user_by_discord_id(db, discord_user_id)
    project = project_repository.find_project_by_discord_channel_id(
        db, discord_channel_id
    )

    data = project_service.get_project(user.id, project.id, db)
    return project_read_success(data)


@router.get(
    "/issues",
    summary="Get all existing issues",
    response_model=SuccessResponse[List[IssueRes]],
)
def get_all_issues(
    discord_channel_id: str = Header(..., description="Discord Channel ID"),
    discord_user_id: str = Header(..., description="Discord User ID"),
    db: Session = Depends(get_db),
):
    user = user_repository.find_user_by_discord_id(db, discord_user_id)
    project = project_repository.find_project_by_discord_channel_id(
        db, discord_channel_id
    )
    data = issue_service.get_all_issues(user.id, project.id, db)
    return issue_read_success(data)


@router.get(
    "/issue/detail",
    summary="Get existing issue",
    response_model=SuccessResponse[IssueRes],
)
def get_issue(
    issue_number: int,
    discord_channel_id: str = Header(..., description="Discord Channel ID"),
    discord_user_id: str = Header(..., description="Discord User ID"),
    db: Session = Depends(get_db),
):
    user = user_repository.find_user_by_discord_id(db, discord_user_id)
    project = project_repository.find_project_by_discord_channel_id(
        db, discord_channel_id
    )
    data = issue_service.get_issue(user.id, project.id, issue_number, db)
    return issue_read_success(data)


@router.post(
    "/issue-reschedule",
    summary="Create a new issue rescheduling",
    response_model=SuccessResponse[IssueReschedulingRes],
)
def create_issue_rescheduling(
    issue_rescheduling_req: IssueReschedulingReq,
    discord_channel_id: str = Header(..., description="Discord Channel ID"),
    discord_user_id: str = Header(..., description="Discord User ID"),
    db: Session = Depends(get_db),
):
    user = user_repository.find_user_by_discord_id(db, discord_user_id)
    project = project_repository.find_project_by_discord_channel_id(
        db, discord_channel_id
    )
    data = issue_rescheduling_service.create_issue_rescheduling(
        user.id, project.id, issue_rescheduling_req, db
    )
    return issue_rescheduling_create_success(data)


@router.post(
    "/test-scheduler",
    summary="Test scheduler function",
)
async def test_scheduler():
    await send_daily_request()
    return
