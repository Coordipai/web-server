from sqlalchemy.orm import Session

from src.common.util.permissions import (
    has_permission_to_access_project,
    has_permission_to_modify_issue_rescheduling,
)
from src.issue import repository as issue_repository
from src.issue.schemas import IssueUpdateReq
from src.issue_rescheduling import repository as issue_rescheduling_repository
from src.issue_rescheduling.models import IssueRescheduling
from src.issue_rescheduling.schemas import (
    IssueReschedulingReq,
    IssueReschedulingRes,
    IssueReschedulingType,
)
from src.project import repository as project_repository
from src.response.error_definitions import (
    InvalidReschedulingType,
    IssueNotFound,
    IssueReschedulingAlreadyExist,
    IssueReschedulingNotFound,
    UserNotFound,
)
from src.user import repository as user_repository


def create_issue_rescheduling(
    user_id: int,
    project_id: int,
    issue_rescheduling_req: IssueReschedulingReq,
    db: Session,
):
    """
    Create a new issue rescheduling
    """
    has_permission_to_access_project(user_id, project_id, db)

    requester = user_repository.find_user_by_user_id(db, user_id)
    if not requester:
        raise UserNotFound()

    existing_issue_rescheduling = issue_rescheduling_repository.find_issue_scheduling_by_project_id_and_issue_number(
        db, project_id, issue_rescheduling_req.issue_number
    )
    if existing_issue_rescheduling:
        raise IssueReschedulingAlreadyExist()

    project = project_repository.find_project_by_id(db, project_id)

    issue = issue_repository.find_issue_by_issue_number(
        user_id, project.repo_fullname, issue_rescheduling_req.issue_number, db
    )
    if not issue:
        raise IssueNotFound()

    issue_rescheduling = IssueRescheduling(
        issue_number=issue_rescheduling_req.issue_number,
        requester=requester.id,
        reason=issue_rescheduling_req.reason,
        new_iteration=issue_rescheduling_req.new_iteration,
        new_assignees=issue_rescheduling_req.new_assignees,
        project_id=project_id,
    )

    saved_issue_rescheduling = issue_rescheduling_repository.create_issue_rescheduling(
        db, issue_rescheduling
    )
    issue_rescheduling_res = IssueReschedulingRes.from_issue(
        saved_issue_rescheduling, requester, issue
    )

    return issue_rescheduling_res


def get_all_issue_reschedulings(user_id: int, project_id: int, db: Session):
    all_existing_issue_reschedulings = (
        issue_rescheduling_repository.find_all_issue_rescheduling_by_project_id(
            db, project_id
        )
    )
    has_permission_to_access_project(user_id, project_id, db)

    project = project_repository.find_project_by_id(db, project_id)

    issue_rescheduling_res_list = []
    for issue_rescheduling in all_existing_issue_reschedulings:
        issue = issue_repository.find_issue_by_issue_number(
            user_id, project.repo_fullname, issue_rescheduling.issue_number, db
        )
        if not issue:
            raise IssueNotFound()

        requester = user_repository.find_user_by_user_id(
            db, issue_rescheduling.requester
        )
        if not requester:
            raise UserNotFound()

        issue_rescheduling_res = IssueReschedulingRes.from_issue(
            issue_rescheduling, requester, issue
        )
        issue_rescheduling_res_list.append(issue_rescheduling_res)

    return issue_rescheduling_res_list


def update_issue_rescheduling(
    user_id: int,
    project_id: int,
    issue_rescheduling_req: IssueReschedulingReq,
    db: Session,
):
    """
    Update the existing issue rescheduling by project id and issue number
    """
    existing_issue_rescheduling = issue_rescheduling_repository.find_issue_scheduling_by_project_id_and_issue_number(
        db, project_id, issue_rescheduling_req.issue_number
    )
    if not existing_issue_rescheduling:
        raise IssueReschedulingNotFound()

    has_permission_to_modify_issue_rescheduling(
        user_id, existing_issue_rescheduling, db
    )

    project = project_repository.find_project_by_id(db, project_id)

    issue = issue_repository.find_issue_by_issue_number(
        user_id, project.repo_fullname, issue_rescheduling_req.issue_number, db
    )
    if not issue:
        raise IssueNotFound()

    existing_issue_rescheduling.reason = issue_rescheduling_req.reason
    existing_issue_rescheduling.new_iteration = issue_rescheduling_req.new_iteration
    existing_issue_rescheduling.new_assignees = issue_rescheduling_req.new_assignees

    saved_issue_rescheduling = issue_rescheduling_repository.update_issue_rescheduling(
        db, existing_issue_rescheduling
    )

    requester = user_repository.find_user_by_user_id(
        db, saved_issue_rescheduling.requester
    )
    if not requester:
        raise UserNotFound()

    issue_rescheduling_res = IssueReschedulingRes.from_issue(
        saved_issue_rescheduling, requester, issue
    )
    return issue_rescheduling_res


def delete_issue_rescheduling(
    user_id: int, id: int, type: IssueReschedulingType, db: Session
):
    existing_issue_rescheduling = (
        issue_rescheduling_repository.find_issue_scheduling_by_id(db, id)
    )
    if not existing_issue_rescheduling:
        raise IssueReschedulingNotFound()

    has_permission_to_modify_issue_rescheduling(
        user_id, existing_issue_rescheduling, db
    )

    if type == IssueReschedulingType.APPROVED:
        issue = issue_repository.find_issue_by_issue_number(
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

        issue_rescheduling_repository.delete_issue_rescheduling(
            db, user_id, existing_issue_rescheduling, issue_update_req
        )
    elif type == IssueReschedulingType.REJECTED:
        issue_rescheduling_repository.delete_issue_rescheduling(
            db, user_id, existing_issue_rescheduling, None
        )
    else:
        raise InvalidReschedulingType(type)
