from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from src.exceptions.definitions import SQLError
from src.config.logger_config import add_daily_file_handler, setup_logger
from src.models import User

logger = setup_logger(__name__)
add_daily_file_handler(logger)


def create_user(db: Session, user: User) -> User:
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error during user creation: {e}")
        db.rollback()
        raise SQLError()


def find_user_by_github_id(db: Session, github_id: str) -> User | None:
    try:
        result = db.execute(select(User).filter(User.github_id == github_id))
        return result.scalars().first()
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def find_user_by_user_id(db: Session, user_id: str) -> User | None:
    try:
        result = db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()
