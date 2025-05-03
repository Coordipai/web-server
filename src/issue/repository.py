from typing import Optional, Tuple
import requests
import re
from sqlalchemy.orm import Session
from src.issue.schemas import (
    IssueCloseReq,
    IssueCreateReq,
    IssueRes,
    IssueUpdateReq,
)
from src.response.error_definitions import GitHubApiError, InvalidReqFormat
from src.user.repository import find_all_users_by_github_names, find_user_by_user_id
from src.user.schemas import UserRes


def get_github_headers(user_id: int, db: Session):
    user = find_user_by_user_id(db, user_id)
    token = user.github_access_token
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    return headers


def retrieve_hidden_metadata(body: str) -> Optional[Tuple[str, int]]:
    """
    Extract hidden metadata(priority, iteration) from issue body
    ex. <!-- priority: M iteration: 2 -->

    Returns priority="U"(Unknown), iteration=-1(Unknown) if there is no matched patterns
    """
    metadata_pattern = re.compile(
        r"<!--\s*priority:\s*(?P<priority>\w+)\s*\n\s*iteration:\s*(?P<iteration>\d+)\s*-->",
        re.IGNORECASE,
    )

    match = metadata_pattern.search(body)
    if match:
        priority = match.group("priority")
        iteration = int(match.group("iteration"))
        return priority, iteration
    return "U", -1


def add_hidden_metadata(body: str, priority: str, iteration: int) -> str:
    """
    Add or update hidden metadata(priority, iteration) in the issue body
    """
    # Check priority is one of M, S, C, W and iteration is valid integer
    if priority not in ["M", "S", "C", "W"] or iteration < 0:
        raise InvalidReqFormat()
    metadata_pattern = re.compile(r"<!--\s*priority:\s*\w+\s*iteration:\s*\d+\s*-->")

    new_metadata = f"<!--\npriority: {priority}\niteration: {iteration}\n-->"

    if metadata_pattern.search(body):
        # Replace old metadata with new one
        return metadata_pattern.sub(new_metadata, body)
    else:
        # Add metadata below the body
        return f"{body.rstrip()}\n\n{new_metadata}"


def return_issue_res(issue_json, db: Session):
    priority, iteration = retrieve_hidden_metadata(issue_json["body"])

    github_names = [assignee["login"] for assignee in issue_json.get("assignees", [])]
    users = find_all_users_by_github_names(db, github_names)
    assignees = [UserRes.model_validate(user) for user in users]

    issue_res = IssueRes(
        repo_fullname=issue_json["repository_url"].split("repos/")[-1],
        issue_number=int(issue_json["number"]),
        title=issue_json["title"],
        body=issue_json["body"],
        assignees=assignees,
        priority=priority,
        iteration=iteration,
        labels=[label["name"] for label in issue_json.get("labels", [])],
    )
    return issue_res


def create_issue(user_id: int, issue_req: IssueCreateReq, db: Session):
    repos_url = f"https://api.github.com/repos/{issue_req.repo_fullname}/issues"
    req_data = {
        "title": issue_req.title,
        "body": add_hidden_metadata(
            issue_req.body, issue_req.priority, issue_req.iteration
        ),
        "assignees": issue_req.assignees,
        "labels": issue_req.labels,
    }

    issue_response = requests.post(
        repos_url, headers=get_github_headers(user_id, db), json=req_data
    )

    if issue_response.status_code != 201:
        raise GitHubApiError(issue_response.status_code)

    issue_json = issue_response.json()
    return return_issue_res(issue_json, db)


def find_issue_by_issue_number(
    user_id: int, repo_fullname: str, issue_number: int, db: Session
):
    repos_url = f"https://api.github.com/repos/{repo_fullname}/issues/{issue_number}"
    issue_response = requests.get(repos_url, headers=get_github_headers(user_id, db))

    if issue_response.status_code != 200:
        raise GitHubApiError(issue_response.status_code)

    issue_json = issue_response.json()
    return return_issue_res(issue_json, db)


def update_issue(user_id: int, issue_req: IssueUpdateReq, db: Session):
    repos_url = f"https://api.github.com/repos/{issue_req.repo_fullname}/issues/{issue_req.issue_number}"
    req_data = {
        "title": issue_req.title,
        "body": add_hidden_metadata(
            issue_req.body, issue_req.priority, issue_req.iteration
        ),
        "assignees": issue_req.assignees,
        "labels": issue_req.labels,
    }

    issue_response = requests.patch(
        repos_url, headers=get_github_headers(user_id, db), json=req_data
    )

    if issue_response.status_code != 200:
        raise GitHubApiError(issue_response.status_code)

    issue_json = issue_response.json()
    return return_issue_res(issue_json, db)


def close_issue(user_id: int, issue_req: IssueCloseReq, db: Session):
    repos_url = f"https://api.github.com/repos/{issue_req.repo_fullname}/issues/{issue_req.issue_number}"
    req_data = {
        "state": "close",
    }

    issue_response = requests.patch(
        repos_url, headers=get_github_headers(user_id, db), json=req_data
    )

    if issue_response.status_code != 200:
        raise GitHubApiError(issue_response.status_code)
