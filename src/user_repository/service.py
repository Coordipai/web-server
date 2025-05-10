from typing import List

from sqlalchemy.orm import Session

from src.stat.service import get_repositories
from src.user.repository import find_user_by_user_id
from src.user_repository.schemas import UserRepositoryReq, UserRepositoryRes
from user_repository import repository


def sync_user_repositories(
    user_id: int, user_repository_req_list: List[UserRepositoryReq], db: Session
):
    """
    Sync selected user repositories

    Returns selected user repositories
    """
    repo_names = [r.repo_fullname for r in user_repository_req_list]
    repository.sync_user_repositories(db, user_id, repo_names)


def get_all_selected_repositories(user_id: int, db: Session):
    """
    Get all existing selected repositories

    Returns selected user repositories
    """
    user_repositories = repository.find_all_repositories_by_user_id(db, user_id)

    selected_repository_list = []
    for user_repo in user_repositories:
        user_repository_res = UserRepositoryRes(repo_fullname=user_repo.repo_fullname)
        selected_repository_list.append(user_repository_res)
    return selected_repository_list


def get_all_repositories_from_github(user_id: int, db: Session):
    user = find_user_by_user_id(db, user_id)
    repo_list = get_repositories(user.github_access_token)
    return [UserRepositoryRes(repo_fullname=repo["name"]) for repo in repo_list]
