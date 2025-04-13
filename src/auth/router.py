from fastapi.responses import RedirectResponse
from database import get_db
from fastapi import APIRouter, Depends, Request, Response

from src.config import GITHUB_CLIENT_ID, GITHUB_REDIRECT_URI
from auth import service

router = APIRouter(prefix="/auth", tags=["GitHub OAuth"])

GITHUB_OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"


@router.get("/login", summary="Redirect to GitHub login page")
def login_with_github():
    """
    Redirect to GitHub OAuth
    """
    github_url = (
        f"{GITHUB_OAUTH_AUTHORIZE_URL}"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        "&scope=repo user"
    )
    return RedirectResponse(github_url, status_code=302)


@router.get("/github/callback", summary="Callback for GitHub login")
async def github_callback(request: Request, response: Response):
    return await service.github_callback(request, response)


# TODO Register new user
# TODO Refresh token
# TODO Logout
# TODO Unregister
