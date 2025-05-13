from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from src.config.logger_config import add_daily_file_handler, setup_logger
from src.models import User
from src.response.error_definitions import SQLError

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


def find_all_users_by_github_names(db: Session, github_names: list[str]) -> User | None:
    try:
        result = db.query(User).filter(User.github_name.in_(github_names)).all()
        return result
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


def update_user_stat(db: Session, user: User, stat: dict) -> User:
    try:
        user.stat = stat
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def update_user(db: Session, user: User) -> User:
    try:
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def delete_user(db: Session, user: User):
    try:
        db.delete(user)
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()
