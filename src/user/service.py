from sqlalchemy.orm import Session

from auth.util.redis import get_token_from_redis
from src.models import User
from src.response.error_definitions import UserAlreadyExist, UserNotFound
from user import repository
from user.schemas import UserReq, UserRes


async def create_user(db: Session, user_req: UserReq):
    """
    Create new user
    """
    existing_user = repository.find_user_by_github_id(db, user_req.github_id)
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

    saved_user = repository.create_user(db, new_user)
    return saved_user


async def update_user(db: Session, user_req: UserReq):
    """
    Update existing user
    """
    existing_user = repository.find_user_by_github_id(db, user_req.github_id)
    if not existing_user:
        raise UserNotFound()

    existing_user.name = user_req.name
    existing_user.discord_id = user_req.discord_id
    existing_user.github_name = user_req.github_name
    existing_user.category = user_req.category
    existing_user.career = user_req.career
    existing_user.profile_img = user_req.profile_img

    updated_user = repository.update_user(db, existing_user)
    return updated_user


def search_users_by_name(user_name: str, db: Session):
    users = db.query(User).filter(User.name.ilike(f"%{user_name}%")).all()
    user_res_list = []

    for user in users:
        user_res = UserRes.model_validate(user)
        user_res_list.append(user_res)

    return user_res_list
