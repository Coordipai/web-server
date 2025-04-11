from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from src.auth import service, config, schemas

router = APIRouter(prefix="/auth/github", tags=["GitHub OAuth"])

GITHUB_OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"

@router.get("/login", summary="Redirect to GitHub login page")
def login_with_github():
    github_url = (
        f"{GITHUB_OAUTH_AUTHORIZE_URL}"
        f"?client_id={config.GITHUB_CLIENT_ID}"
        f"&redirect_uri={config.REDIRECT_URI}"
        "&scope=repo user"
    )
    return RedirectResponse(github_url)

@router.get("/callback", response_model=schemas.GitHubAuthResponse, summary="Callback for GitHub login")
async def github_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No code provided"}

    access_token = await service.exchange_code_for_token(code)
    if not access_token:
        return {"error": "Failed to get access token"}

    user = await service.get_github_user(access_token)
    repos = await service.get_user_repos(access_token)

    return schemas.GitHubAuthResponse(
        user=user,
        repositories=[
            schemas.RepoInfo(
                name=repo["name"],
                private=repo["private"],
                url=repo["html_url"],
                description=repo.get("description"),
            )
            for repo in repos
        ]
    )
