from sqlalchemy.orm import Session

from src.issue.repository import find_issue_by_issue_number
from src.issue.schemas import IssueUpdateReq
from src.issue_rescheduling import repository
from src.issue_rescheduling.models import IssueRescheduling
from src.issue_rescheduling.schemas import (
    IssueReschedulingReq,
    IssueReschedulingRes,
    IssueReschedulingType,
)
from src.response.error_definitions import (
    InvalidReschedulingType,
    IssueReschedulingAlreadyExist,
    IssueReschedulingNotFound,
)


def create_issue_rescheduling(
    issue_rescheduling_req: IssueReschedulingReq,
    db: Session,
):
    """
    Create a new issue rescheduling
    """
    existing_issue_rescheduling = (
        repository.find_issue_scheduling_by_project_id_and_issue_number(
            db, issue_rescheduling_req.project_id, issue_rescheduling_req.issue_number
        )
    )

    if existing_issue_rescheduling:
        raise IssueReschedulingAlreadyExist()

    issue_rescheduling = IssueRescheduling(
        issue_number=issue_rescheduling_req.issue_number,
        reason=issue_rescheduling_req.reason,
        new_iteration=issue_rescheduling_req.new_iteration,
        new_assignees=issue_rescheduling_req.new_assignees,
        project_id=issue_rescheduling_req.project_id,
    )

    saved_issue_rescheduling = repository.create_issue_rescheduling(
        db, issue_rescheduling
    )
    issue_rescheduling_res = IssueReschedulingRes.model_validate(
        saved_issue_rescheduling
    )
    return issue_rescheduling_res


def get_all_issue_reschedulings(project_id: int, db: Session):
    all_existing_issue_reschedulings = (
        repository.find_all_issue_rescheduling_by_project_id(db, project_id)
    )
    issue_rescheduling_res_list = []
    for issue_rescheduling in all_existing_issue_reschedulings:
        issue_rescheduling_res = IssueReschedulingRes.model_validate(issue_rescheduling)
        issue_rescheduling_res_list.append(issue_rescheduling_res)

    return issue_rescheduling_res_list


def update_issue_rescheduling(
    issue_rescheduling_req: IssueReschedulingReq, db: Session
):
    """
    Update the existing issue rescheduling by project id and issue number
    """
    existing_issue_rescheduling = (
        repository.find_issue_scheduling_by_project_id_and_issue_number(
            db, issue_rescheduling_req.project_id, issue_rescheduling_req.issue_number
        )
    )

    if not existing_issue_rescheduling:
        raise IssueReschedulingNotFound()

    existing_issue_rescheduling.reason = issue_rescheduling_req.reason
    existing_issue_rescheduling.new_iteration = issue_rescheduling_req.new_iteration
    existing_issue_rescheduling.new_assignees = issue_rescheduling_req.new_assignees

    saved_issue_rescheduling = repository.update_issue_rescheduling(
        db, existing_issue_rescheduling
    )
    issue_rescheduling_res = IssueReschedulingRes.model_validate(
        saved_issue_rescheduling
    )
    return issue_rescheduling_res


def delete_issue_rescheduling(
    user_id: int, id: int, type: IssueReschedulingType, db: Session
):
    if type == IssueReschedulingType.APPROVED:
        existing_issue_rescheduling = repository.find_issue_scheduling_by_id(db, id)

        issue = find_issue_by_issue_number(
            user_id,
            existing_issue_rescheduling.project.repo_fullname,
            existing_issue_rescheduling.issue_number,
            db,
        )
        issue_update_req = IssueUpdateReq(
            project_id=existing_issue_rescheduling.project_id,
            issue_number=issue.issue_number,
            title=issue.title,
            body=issue.body,
            assignees=existing_issue_rescheduling.new_assignees,
            priority=issue.priority,
            iteration=existing_issue_rescheduling.new_iteration,
            labels=issue.labels,
        )

        repository.delete_issue_rescheduling(db, user_id, existing_issue_rescheduling, issue_update_req)

    elif type == IssueReschedulingType.REJECTED:
        existing_issue_rescheduling = repository.find_issue_scheduling_by_id(db, id)
        repository.delete_issue_rescheduling(db, existing_issue_rescheduling)
    else:
        raise InvalidReschedulingType(type)
