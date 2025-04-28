from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from user import service

from src.database import get_db

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/search", summary="Search user by name")
def search_users(user_name: str, db: Session = Depends(get_db)):
    return service.search_users_by_name(user_name, db)
