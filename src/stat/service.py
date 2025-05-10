import requests

from src.response.error_definitions import GitHubApiError


def get_repositories(token):
    """
    Get all repositories the user owns, collaborates on, or is a member of the organization for
    """
    headers = {"Authorization": f"token {token}"}
    repos_url = f"https://api.github.com/user/repos?visibility=all&affiliation=owner,collaborator,organization_member"
    repos_response = requests.get(repos_url, headers=headers)
    repos_json = repos_response.json()

    repo_list = []
    for repo in repos_json:
        data = {
            "name": repo["full_name"],
            "private": repo["private"],
            "owner": repo["owner"]["login"],
            "url": repo["html_url"],
        }
        repo_list.append(data)

    if repos_response.status_code != 200:
        raise GitHubApiError(repos_response.status_code)

    return repo_list


def get_pull_requests(repo_fullname, user_name, token):
    """
    Get all pull requests owned by user
    """
    headers = {"Authorization": f"token {token}"}
    prs_url = f"https://api.github.com/repos/{repo_fullname}/pulls?state=all"
    prs_response = requests.get(prs_url, headers=headers)

    if prs_response.status_code != 200:
        raise GitHubApiError(prs.response.status_code)

    prs = prs_response.json()

    pr_list = []
    for pr in prs:
        if pr["user"]["login"] == user_name and pr["merged_at"]:
            pr_details_url = pr["url"]
            pr_details_response = requests.get(pr_details_url, headers=headers)

            if pr_details_response.status_code != 200:
                raise GitHubApiError(pr_details_response.status_code)

            pr_details = pr_details_response.json()

            # Parse related_issues (close # format)
            body = pr_details.get("body", "")  # Set blank if body is empty
            body = body if body is not None else ""

            related_issues = []
            for line in body.splitlines():
                if line.startswith("close #"):
                    try:
                        issue_number = int(line.split("#")[1].strip())
                        related_issues.append(issue_number)
                    except (ValueError, IndexError):
                        pass

            pr_list.append(
                {
                    "repository": repo_fullname,
                    "pull_request_number": pr["number"],
                    "author": user_name,
                    "title": pr["title"],
                    "body": body,
                    "related_issues": related_issues,
                    "created_at": pr["created_at"],
                    "merged_at": pr["merged_at"],
                }
            )

    return pr_list


def get_commits(repo_fullname, user_name, token):
    headers = {"Authorization": f"token {token}"}
    commits_url = (
        f"https://api.github.com/repos/{repo_fullname}/commits?author={user_name}"
    )
    commits_response = requests.get(commits_url, headers=headers)

    if commits_response.status_code != 200:
        if commits_response.json()["message"] == "Git Repository is empty.":
            return []
        raise GitHubApiError(commits_response.status_code)

    commits = commits_response.json()

    commit_list = []
    for commit in commits:
        commit_list.append(commit["commit"]["message"])

    return commit_list
