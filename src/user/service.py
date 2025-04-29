from sqlalchemy.orm import Session
from src.exceptions.definitions import UserAlreadyExist
from src.models import User
from user.schemas import UserReq, UserRes
from user import repository
from src.models import User
from auth.util.redis import get_token_from_redis


async def create_user(db: Session, user_req: UserReq) -> UserRes:
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
    )

    saved_user = repository.create_user(db, new_user)
    return saved_user


def search_users_by_name(db: Session, user_name: str):
    users = db.query(User).filter(User.username.ilike(f"%{user_name}%")).all()
    user_res_list = []

    for user in users:
        user_res = UserRes.model_validate(user)
        user_res_list.append(user_res)

    return user_res_list
