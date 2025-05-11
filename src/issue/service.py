from sqlalchemy.orm import Session

from src.issue import repository
from src.issue.schemas import (
    IssueCloseReq,
    IssueCreateReq,
    IssueUpdateReq,
    ProjectIssueSummary,
)
from src.project.repository import find_project_by_id


def create_issue(user_id: int, issue_req: IssueCreateReq, db: Session):
    """
    Create a new issue in GitHub

    Returns issue data
    """
    project = find_project_by_id(db, issue_req.project_id)
    return repository.create_issue(user_id, project.repo_fullname, issue_req, db)


def get_issue(user_id: int, project_id: int, issue_number: int, db: Session):
    """
    Get the existing issue by issue number from GitHub

    Returns issue data
    """
    project = find_project_by_id(db, project_id)
    return repository.find_issue_by_issue_number(
        user_id, project.repo_fullname, issue_number, db
    )


def get_project_issue_summary(
    user_id: int, project_id: int, db: Session
) -> ProjectIssueSummary:
    """
    Get summary of project issues (number of opend/closed/all issues)
    """
    project = find_project_by_id(db, project_id)
    all_issues = repository.find_all_issues_by_project_id(
        user_id, project.repo_fullname, db
    )

    opened_issues = 0
    closed_issues = 0

    for issue in all_issues:
        if issue.closed:
            closed_issues += 1
        else:
            opened_issues += 1

    summary = ProjectIssueSummary(
        opened_issues=opened_issues,
        closed_issues=closed_issues,
        all_issues=opened_issues + closed_issues,
    )
    return summary


def get_all_issues(user_id: int, project_id: int, db: Session):
    """
    Get all existing issues in project

    Returns list of issue data
    """
    project = find_project_by_id(db, project_id)
    return repository.find_all_issues_by_project_id(user_id, project.repo_fullname, db)


def update_issue(user_id: int, issue_req: IssueUpdateReq, db: Session):
    """
    Update the existing issue by issue number in GitHub

    Returns issue data
    """
    project = find_project_by_id(db, issue_req.project_id)
    return repository.update_issue(user_id, project.repo_fullname, issue_req, db)


def close_issue(user_id: int, issue_req: IssueCloseReq, db: Session):
    """
    Close the existing issue by issue number in GitHub

    Returns issue data
    """
    project = find_project_by_id(db, issue_req.project_id)
    repository.close_issue(user_id, project.repo_fullname, issue_req, db)
