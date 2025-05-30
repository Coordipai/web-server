from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from src.config.logger_config import add_daily_file_handler, setup_logger
from src.issue.repository import update_issue
from src.issue.schemas import IssueUpdateReq
from src.issue_rescheduling.models import IssueRescheduling
from src.response.error_definitions import IssueReschedulingNotFound, SQLError

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


def find_issue_scheduling_by_id(db: Session, issue_rescheduling_id: int):
    try:
        result = db.execute(
            select(IssueRescheduling).filter(
                IssueRescheduling.id == issue_rescheduling_id
            )
        )
        issue_rescheduling = result.scalars().first()
        if not issue_rescheduling:
            raise IssueReschedulingNotFound()
        return issue_rescheduling
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def find_issue_scheduling_by_project_id_and_issue_number(
    db: Session, project_id: int, issue_number: int
) -> IssueRescheduling | None:
    try:
        result = db.execute(
            select(IssueRescheduling).filter(
                IssueRescheduling.project_id == project_id
                and IssueRescheduling.issue_number == issue_number
            )
        )
        return result.scalars().first()
    except NoResultFound:
        raise IssueReschedulingNotFound()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()


def find_all_issue_rescheduling_by_project_id(db: Session, project_id: int):
    try:
        result = (
            db.query(IssueRescheduling)
            .filter(IssueRescheduling.project_id.in_([project_id]))
            .all()
        )
        return result
    except NoResultFound:
        raise IssueReschedulingNotFound()
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


def delete_issue_rescheduling(db: Session, user_id: int, issue_rescheduling: IssueRescheduling, issue_update_req: IssueUpdateReq | None):
    try:
        if issue_update_req:
            update_issue(
                user_id,
                issue_rescheduling.project.repo_fullname,
                issue_update_req,
                db,
            )
        db.delete(issue_rescheduling)
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()
