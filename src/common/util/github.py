import requests
from sqlalchemy.orm import Session

from src.response.error_definitions import GitHubApiError
from src.user.repository import find_user_by_user_id

GITHUB_URL = "https://api.github.com"


def get_github_access_token_from_user(user_id: int, db: Session):
    """
    Returns GitHub AccessToken saved in our DB.
    """
    user = find_user_by_user_id(db, user_id)
    token = user.github_access_token
    return token


def get_github_headers(user_id: int, db: Session):
    """
    Returns Header info for GitHub API request.
    """
    token = get_github_access_token_from_user(user_id, db)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    return headers


def check_github_repo_exists(user_id: int, repo_fullname: str, db: Session) -> bool:
    """
    Check if GitHub repository exists.
    """
    api_url = f"{GITHUB_URL}/repos/{repo_fullname}"

    try:
        response = requests.get(api_url, headers=get_github_headers(user_id, db))

        if response.status_code == 200:
            return True  # Repository exists
        elif response.status_code == 404:
            return False  # Repository not found
        else:
            raise GitHubApiError(response.status_code)

    except requests.exceptions.RequestException as e:
        raise GitHubApiError(response.status_code)
