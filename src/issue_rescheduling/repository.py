from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from src.issue_rescheduling.models import IssueRescheduling
from src.response.error_definitions import SQLError
from src.config.logger_config import add_daily_file_handler, setup_logger

logger = setup_logger(__name__)
add_daily_file_handler(logger)


def create_issue_rescheduling(
    db: Session, data: IssueRescheduling
) -> IssueRescheduling:
    try:
        db.add(data)
        db.commit()
        db.refresh(data)
        return data
    except SQLAlchemyError as e:
        logger.error(f"Database error during issue rescheduling creation: {e}")
        db.rollback()
        raise SQLError()


def find_all_issue_rescheduling_by_project_id(db: Session, project_id: int):
    try:
        result = (
            db.query(IssueRescheduling)
            .filter(IssueRescheduling.project_id.in_(project_id))
            .all()
        )
        return result
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error during issue rescheduling retrive: {e}")
        db.rollback()
        raise SQLError()


def update_issue_rescheduling(
    db: Session, data: IssueRescheduling
) -> IssueRescheduling:
    try:
        db.commit()
        db.refresh(data)
        return data
    except SQLAlchemyError as e:
        logger.error(f"Database error during issue rescheduling update: {e}")
        db.rollback()
        raise SQLError()
