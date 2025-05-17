from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.config.logger_config import add_daily_file_handler, setup_logger
from src.models import ProjectUser
from src.response.error_definitions import SQLError

logger = setup_logger(__name__)
add_daily_file_handler(logger)


def create_project_user(db: Session, project_user: ProjectUser) -> ProjectUser:
    try:
        db.add(project_user)
        db.commit()
        db.refresh(project_user)
        return project_user
    except SQLAlchemyError as e:
        logger.error(f"Database error during project_user creation: {e}")
        db.rollback()
        raise SQLError()


def find_all_projects_by_user_id(db: Session, user_id: int) -> list[ProjectUser]:
    try:
        result = db.execute(select(ProjectUser).filter(ProjectUser.user_id == user_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()
