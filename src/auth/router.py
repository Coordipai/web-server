from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth import service
from auth.schemas import AuthReq, AuthRes, RefreshReq
from src.config.config import GITHUB_CLIENT_ID, GITHUB_REDIRECT_URI
from src.config.database import get_db
from src.response.schemas import SuccessResponse
from src.response.success_definitions import (
    login_success,
    logout_success,
    refresh_token_success,
    register_success,
)

GITHUB_OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"

router = APIRouter(prefix="/auth", tags=["GitHub OAuth"])


@router.get("/github/login", summary="Redirect to GitHub login page")
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
async def github_callback(request: Request, db: Session = Depends(get_db)):
    return await service.github_callback(request, db)


@router.post(
    "/register", summary="Register new user", response_model=SuccessResponse[AuthRes]
)
async def register(
    auth_req: AuthReq,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(None),
):
    data = await service.register(db, auth_req, access_token)
    return register_success(data)


@router.post(
    "/login", summary="Login existing user", response_model=SuccessResponse[AuthRes]
)
async def login(
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(None),
):
    data = await service.login(db, access_token)
    return login_success(data)


@router.post(
    "/refresh",
    summary="Get new token using refresh token",
    response_model=SuccessResponse[AuthRes],
)
async def refresh(refresh_token: RefreshReq, db: Session = Depends(get_db)):
    data = await service.refresh(db, refresh_token.refresh_token)
    return refresh_token_success(data)


@router.post(
    "/logout",
    summary="Get new token using refresh token",
    response_model=SuccessResponse,
)
async def logout(request: Request):
    user_id = request.state.user_id
    await service.logout(user_id)
    return logout_success()


# TODO Unregister
