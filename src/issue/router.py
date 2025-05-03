from fastapi import APIRouter, Request
from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.issue import service
from src.issue.schemas import (
    IssueCloseReq,
    IssueCreateReq,
    IssueGetReq,
    IssueRes,
    IssueUpdateReq,
)
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    issue_close_success,
    issue_create_success,
    issue_read_success,
    issue_update_success,
)


router = APIRouter(prefix="/issue", tags=["Issue"])


@router.post(
    "/", summary="Create a new issue", response_model=SuccessResponse[IssueRes]
)
def create_issue(
    request: Request, issue_req: IssueCreateReq, db: Session = Depends(get_db)
):
    user_id = request.state.user_id
    data = service.create_issue(user_id, issue_req, db)
    return issue_create_success(data)


@router.get(
    "/{owner}/{repo}/{issue_number}",
    summary="Get existing issue",
    response_model=SuccessResponse[IssueRes],
)
def get_issue(
    request: Request,
    owner: str,
    repo: str,
    issue_number: int,
    db: Session = Depends(get_db),
):
    user_id = request.state.user_id
    data = service.get_issue(user_id, f"{owner}/{repo}", issue_number, db)
    return issue_read_success(data)


@router.put(
    "/", summary="Update the existing issue", response_model=SuccessResponse[IssueRes]
)
def update_issue(
    request: Request, issue_req: IssueUpdateReq, db: Session = Depends(get_db)
):
    user_id = request.state.user_id
    data = service.update_issue(user_id, issue_req, db)
    return issue_update_success(data)


@router.patch("/", summary="Close the existing issue", response_model=SuccessResponse)
def close_issue(
    request: Request, issue_req: IssueCloseReq, db: Session = Depends(get_db)
):
    user_id = request.state.user_id
    service.close_issue(user_id, issue_req, db)
    return issue_close_success()
