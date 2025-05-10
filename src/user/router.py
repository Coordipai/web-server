from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.response.schemas import SuccessResponse
from src.response.success_definitions import user_search_success
from src.user.schemas import UserRes
from user import service

router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "/search",
    summary="Search user by name",
    response_model=SuccessResponse[List[UserRes]],
)
def search_users(user_name: str, db: Session = Depends(get_db)):
    data = service.search_users_by_name(user_name, db)
    return user_search_success(data)
