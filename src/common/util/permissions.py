from sqlalchemy.orm import Session

from src.issue_rescheduling.models import IssueRescheduling
from src.project import repository as project_repository
from src.response.error_definitions import (
    IssueReschedulingPermissionDenied,
    ProjectNotFound,
    ProjectPermissionDenied,
)


def has_permission_to_access_project(user_id: int, project_id: int, db: Session):
    existing_project = project_repository.find_project_by_id(db, project_id)
    if not existing_project:
        raise ProjectNotFound()

    is_owner = existing_project.owner == user_id
    is_member = project_repository.is_project_member(db, project_id, user_id)

    if not (is_owner or is_member):
        raise ProjectPermissionDenied()
    return True


def has_permission_to_modify_project(user_id: int, project_id: int, db: Session):
    existing_project = project_repository.find_project_by_id(db, project_id)
    if not existing_project:
        raise ProjectNotFound()

    is_owner = existing_project.owner == user_id

    if not is_owner:
        raise ProjectPermissionDenied()
    return True


def has_permission_to_modify_issue_rescheduling(
    user_id: int, issue_rescheduling: IssueRescheduling, db: Session
):
    existing_project = project_repository.find_project_by_id(
        db, issue_rescheduling.project_id
    )
    if not existing_project:
        raise ProjectNotFound()

    if user_id == existing_project.owner:
        return True

    print(user_id)
    print(type(user_id))
    print(issue_rescheduling.requester)
    print(type(issue_rescheduling.requester))
    print(user_id == issue_rescheduling.requester)

    if user_id != issue_rescheduling.requester:
        raise IssueReschedulingPermissionDenied()

    return True
