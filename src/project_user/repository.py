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
