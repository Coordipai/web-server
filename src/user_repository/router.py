from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    user_repository_from_github_read_success,
    user_repository_read_success,
    user_repository_sync_success,
)
from user_repository import service
from src.user_repository.schemas import UserRepositoryReq, UserRepositoryRes

router = APIRouter(prefix="/user-repo", tags=["User Repository"])


@router.post(
    "/",
    summary="Create a new repository",
    response_model=SuccessResponse[UserRepositoryRes],
)
def sync_user_repositories(
    request: Request,
    user_repository_req_list: List[UserRepositoryReq],
    db: Session = Depends(get_db),
):
    user_id = request.state.user_id
    service.sync_user_repositories(user_id, user_repository_req_list, db)
    data = service.get_all_selected_repositories(user_id, db)
    return user_repository_sync_success(data)


@router.get(
    "/",
    summary="Get all existing selected repository",
    response_model=SuccessResponse[List[UserRepositoryRes]],
)
def get_all_selected_repositories(request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    data = service.get_all_selected_repositories(user_id, db)
    return user_repository_read_success(data)


@router.get(
    "/github",
    summary="Get all repositories from GitHub",
    response_model=SuccessResponse[List[UserRepositoryRes]],
)
def get_all_repositories_from_github(request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    data = service.get_all_repositories_from_github(user_id, db)
    return user_repository_from_github_read_success(data)
