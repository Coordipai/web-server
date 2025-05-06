from typing import List
from fastapi import APIRouter, Request
from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.issue_rescheduling import service

from src.issue_rescheduling.schemas import IssueReschedulingReq, IssueReschedulingRes
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    issue_rescheduling_create_success,
    issue_rescheduling_delete_success,
    issue_rescheduling_read_success,
    issue_rescheduling_update_success,
)


router = APIRouter(prefix="/issue-reschedule", tags=["Issue Rescheduling"])


@router.post(
    "/",
    summary="Create a new issue rescheduling",
    response_model=SuccessResponse[IssueReschedulingRes],
)
def create_issue_rescheduling(
    issue_rescheduling_req: IssueReschedulingReq,
    db: Session = Depends(get_db),
):
    data = service.create_issue_rescheduling(issue_rescheduling_req, db)
    return issue_rescheduling_create_success(data)


@router.get(
    "/{project_id}",
    summary="Get all existing issue reschedulings",
    response_model=SuccessResponse[List[IssueReschedulingRes]],
)
def get_all_issue_reschedulings(
    project_id: int,
    db: Session = Depends(get_db),
):
    data = service.get_all_issue_reschedulings(project_id, db)
    return issue_rescheduling_read_success(data)


@router.put(
    "/",
    summary="Update the existing issue rescheduling",
    response_model=SuccessResponse[IssueReschedulingRes],
)
def update_issue_rescheduling(
    issue_rescheduling_req: IssueReschedulingReq,
    db: Session = Depends(get_db),
):
    data = service.update_issue_rescheduling(issue_rescheduling_req, db)
    return issue_rescheduling_update_success(data)


@router.delete(
    "/{id}",
    summary="Delete the existing issue rescheduling",
    response_model=SuccessResponse,
)
def delete_issue_rescheduling(
    id: int,
    db: Session = Depends(get_db),
):
    service.delete_issue_rescheduling(id, db)
    return issue_rescheduling_delete_success()
