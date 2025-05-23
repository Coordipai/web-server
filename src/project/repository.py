from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from src.config.logger_config import add_daily_file_handler, setup_logger
from src.models import Project
from src.response.error_definitions import SQLError

logger = setup_logger(__name__)
add_daily_file_handler(logger)


def create_project(db: Session, project: Project) -> Project:
    try:
        db.add(project)
        db.flush()
        return project
    except SQLAlchemyError as e:
        logger.error(f"Database error during project creation: {e}")
        raise SQLError()


def find_project_by_id(db: Session, project_id: int) -> Project | None:
    try:
        result = db.execute(select(Project).filter(Project.id == project_id))
        return result.scalars().first()
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def find_project_by_name(db: Session, project_name: str) -> Project | None:
    try:
        result = db.execute(select(Project).filter(Project.name == project_name))
        return result.scalars().first()
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def find_project_by_owner(db: Session, owner: str) -> list[Project]:
    try:
        result = db.execute(select(Project).filter(Project.owner == owner))
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def update_project(db: Session, project: Project) -> Project:
    try:
        db.commit()
        db.refresh(project)
        return project
    except SQLAlchemyError as e:
        logger.error(f"Database error during project creation: {e}")
        db.rollback()
        raise SQLError()


def delete_project(db: Session, project: Project):
    try:
        db.delete(project)
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()
