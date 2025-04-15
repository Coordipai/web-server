from typing import Optional
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Cookie, Request, Response
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import GITHUB_CLIENT_ID, GITHUB_REDIRECT_URI
from auth import service
from auth.schemas import AuthReq, AuthRes
from src.database import get_db

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
async def github_callback(request: Request, db: AsyncSession = Depends(get_db)):
    return await service.github_callback(request, db)


@router.post("/login", summary="Login existing user")
async def login(
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None),
) -> AuthRes:
    return await service.login(db, access_token)


@router.post("/register", summary="Register new user")
async def register(
    auth_req: AuthReq,
    db: AsyncSession = Depends(get_db),
    access_token: Optional[str] = Cookie(None),
) -> AuthRes:
    return await service.register(db, auth_req, access_token)


@router.post("/refresh", summary="Get new token using refresh token")
async def refresh(refresh_token: str, db: AsyncSession = Depends(get_db)):
    return await service.refresh(db, refresh_token)


@router.post("/logout", summary="Get new token using refresh token")
async def logout(access_token: str):
    return await service.logout(access_token)


# TODO Unregister
