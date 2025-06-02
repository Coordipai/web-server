from sqlalchemy.orm import Session

from auth.service import REFRESH_TOKEN_REDIS
from auth.util.redis import delete_token_from_redis, get_token_from_redis
from src.models import User
from src.project import repository as project_repository
from src.project_user import repository as project_user_repository
from src.response.error_definitions import (
    ProjectUserExist,
    UserAlreadyExist,
    UserNotFound,
)
from src.user import repository as user_repository
from src.user.schemas import UserReq, UserRes
from src.user_repository import repository as user_repository_repository


async def create_user(db: Session, user_req: UserReq):
    """
    Create new user
    """
    existing_user = user_repository.find_user_by_github_id(db, user_req.github_id)
    if existing_user:
        raise UserAlreadyExist()

    github_access_token = await get_token_from_redis("github_oauth", user_req.github_id)

    new_user = User(
        name=user_req.name,
        discord_id=user_req.discord_id,
        github_id=user_req.github_id,
        github_name=user_req.github_name,
        github_access_token=github_access_token,
        category=user_req.category,
        career=user_req.career,
        profile_img=user_req.profile_img,
    )

    saved_user = user_repository.create_user(db, new_user)
    return saved_user


async def update_user(db: Session, user_req: UserReq):
    """
    Update existing user
    """
    existing_user = user_repository.find_user_by_github_id(db, user_req.github_id)
    if not existing_user:
        raise UserNotFound()

    existing_user.name = user_req.name
    existing_user.discord_id = user_req.discord_id
    existing_user.github_name = user_req.github_name
    existing_user.category = user_req.category
    existing_user.career = user_req.career
    existing_user.profile_img = user_req.profile_img

    updated_user = user_repository.update_user(db, existing_user)
    return updated_user


async def update_github_user(db: Session, github_id: str):
    """
    Update existing user info with GitHub info
    """
    existing_user = user_repository.find_user_by_github_id(db, github_id)
    if not existing_user:
        raise UserNotFound()

    github_access_token = await get_token_from_redis("github_oauth", github_id)
    existing_user.github_access_token = github_access_token


def search_users_by_name(user_name: str, db: Session):
    users = db.query(User).filter(User.name.ilike(f"%{user_name}%")).all()
    user_res_list = []

    for user in users:
        user_res = UserRes.model_validate(user)
        user_res_list.append(user_res)

    return user_res_list


async def unregister(user_id: int, db: Session):
    """
    Unregister user and clean up all related data
    """
    # Check if user has project or owns project
    project_list = project_user_repository.find_all_projects_by_user_id(db, user_id)
    owned_project_list = project_repository.find_project_by_owner(db, user_id)
    if project_list or owned_project_list:
        raise ProjectUserExist()

    # Delete user repositories
    user_repository_repository.delete_all_repositories_by_user_id(db, user_id)

    # Delete user from database
    user = user_repository.find_user_by_user_id(db, user_id)
    if not user:
        raise UserNotFound()

    user_repository.delete_user(db, user)

    # Delete tokens from redis
    redis_refresh_token = await get_token_from_redis(REFRESH_TOKEN_REDIS, user_id)
    await delete_token_from_redis(redis_refresh_token)
