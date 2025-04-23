from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models import User


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def find_user_by_github_id(db: Session, github_id: str) -> User | None:
    result = db.execute(select(User).filter(User.github_id == github_id))
    return result.scalars().first()


def find_user_by_user_id(db: Session, user_id: str) -> User | None:
    result = db.execute(select(User).filter(User.user_id == user_id))
    return result.scalars().first()
