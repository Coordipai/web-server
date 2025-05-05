from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from src.response.error_definitions import SQLError
from src.config.logger_config import add_daily_file_handler, setup_logger
from src.models import IssueRescheduleRequest

logger = setup_logger(__name__)
add_daily_file_handler(logger)


def create_issue_reschedule_request(db: Session, issue_reschedule_request: IssueRescheduleRequest) -> IssueRescheduleRequest:
    try:
        db.add(issue_reschedule_request)
        db.commit()
        db.refresh(issue_reschedule_request)
        return issue_reschedule_request
    except SQLAlchemyError as e:
        logger.error(f"Database error during issue reschedule request creation: {e}")
        db.rollback()
        raise SQLError()
    

def find_issue_reschedule_request_by_id(db: Session, request_id: int) -> IssueRescheduleRequest | None:
    try:
        result = db.execute(select(IssueRescheduleRequest).filter(IssueRescheduleRequest.id == request_id))
        return result.scalars().first()
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()
    

def find_issue_reschedule_request_by_issue_num(db: Session, issue_num: int) -> IssueRescheduleRequest | None:
    try:
        result = db.execute(select(IssueRescheduleRequest).filter(IssueRescheduleRequest.issue_num == issue_num))
        return result.scalars().first()
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()
    

def find_issue_reschedule_requests_by_user_id(db: Session ,user_id: int) -> list[IssueRescheduleRequest] | None:
    try:
        result = db.execute(select(IssueRescheduleRequest).filter(IssueRescheduleRequest.assignee == user_id))
        return result.scalars().all()
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise SQLError()
    
    
def delete_issue_reschedule_request(db: Session, issue_reschedule_request: IssueRescheduleRequest):
    try:
        db.delete(issue_reschedule_request)
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error during issue reschedule request deletion: {e}")
        db.rollback()
        raise SQLError()
