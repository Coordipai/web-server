from sqlalchemy.orm import Session

from src.issue import repository
from src.issue.schemas import IssueCloseReq, IssueCreateReq, IssueGetReq, IssueUpdateReq
from src.user.repository import find_user_by_user_id


def request_github_api(user_id: int, url: str, db: Session):
    user = find_user_by_user_id(db, user_id)
    token = user.github_access_token
    headers = {"Authorization": f"token {token}"}


def create_issue(user_id: int, issue_req: IssueCreateReq, db: Session):
    """
    Create a new issue in GitHub

    Returns issue data
    """
    return repository.create_issue(user_id, issue_req, db)


def get_issue(user_id: int, repo_fullname: str, issue_number: int, db: Session):
    """
    Get the existing issue by issue number from GitHub

    Returns issue data
    """
    return repository.find_issue_by_issue_number(
        user_id, repo_fullname, issue_number, db
    )


def update_issue(user_id: int, issue_req: IssueUpdateReq, db: Session):
    """
    Update the existing issue by issue number in GitHub

    Returns issue data
    """
    return repository.update_issue(user_id, issue_req, db)


def close_issue(user_id: int, issue_req: IssueCloseReq, db: Session):
    """
    Close the existing issue by issue number in GitHub

    Returns issue data
    """
    repository.close_issue(user_id, issue_req, db)
