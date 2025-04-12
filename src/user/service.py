from database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

from auth.models import User


def find_user_by_user_id(user_id: str, db: Session = Depends(get_db)):
    """
    Find User by User ID
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    return user


def find_user_by_github_id(github_id: str, db: Session = Depends(get_db)):
    """
    Find User by GitHub ID
    """
    user = db.query(User).filter(User.github_id == github_id).first()
    return user
