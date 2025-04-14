from typing import Optional
from fastapi import Cookie, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, FRONTEND_URL
from auth.util.jwt import create_access_token, create_refresh_token, parse_token
from auth.util.redis import (
    delete_token_from_redis,
    get_token_from_redis,
    save_token_to_redis,
)
from auth.util.github import get_github_access_token, get_github_user_info
from auth.schemas import AuthReq, AuthRes
from src.user.repository import find_user_by_github_id
from src.user.schemas import UserReq, UserRes
from src.user.service import create_user
import logging

GITHUB_OAUTH_REDIS = "github_oauth"
REFRESH_TOKEN_REDIS = "refresh_token"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def github_callback(
    request: Request,
    db: AsyncSession,
):
    """
    Callback function for GitHub OAuth

    Returns resposne with access token
    """
    code = request.query_params.get("code")
    if not code:
        # TODO Raise Custom Exceptions
        raise HTTPException(
            status_code=404, detail="Failed to get GitHub credential code"
        )

    github_access_token = await get_github_access_token(code)
    if not github_access_token:
        # TODO Raise custom Exceptions
        raise HTTPException(
            status_code=404, detail="Failed to get GitHub credential token"
        )

    github_user = await get_github_user_info(github_access_token)
    github_id = github_user["id"]

    # Check if there is user data in db
    existing_user = await find_user_by_github_id(db, github_id)

    if existing_user:
        access_token = create_access_token(github_id)
        redirect = RedirectResponse(url=f"{FRONTEND_URL}/")
        redirect.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            # TODO Activate when deploy
            # secure=True,
            samesite="Lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES,
            path="/",
        )
    else:
        # Save GitHub AccessToken in redis temporary
        await save_token_to_redis(GITHUB_OAUTH_REDIS, github_id, github_access_token)
        access_token = create_access_token(github_id)

        redirect = RedirectResponse(url=f"{FRONTEND_URL}/register")
        redirect.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            # TODO Activate when deploy
            # secure=True,
            samesite="Lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES,
            path="/",
        )

    return redirect


async def register(
    db: AsyncSession, auth_req: AuthReq, access_token: Optional[str] = Cookie(None)
):
    if not access_token:
        # TODO Raise custom exception
        raise HTTPException(status_code=404, detail="GitHub credential info not found")

    github_id = parse_token(access_token)
    github_access_token = await get_token_from_redis(GITHUB_OAUTH_REDIS, github_id)
    github_user = await get_github_user_info(github_access_token)

    new_user = UserReq(
        **auth_req.model_dump(),
        github_id=github_user["id"],
        github_name=github_user["login"],
        github_access_token=github_access_token,
    )

    saved_user = await create_user(db, new_user)
    user_res = UserRes.model_validate(saved_user)

    # Delete github access token stored in redis
    await delete_token_from_redis(github_access_token)

    access_token = create_access_token(saved_user.id)
    refresh_token = create_refresh_token(saved_user.id)

    # Save refresh token in redis
    await save_token_to_redis(REFRESH_TOKEN_REDIS, saved_user.id, refresh_token)

    return AuthRes(
        user=user_res, access_token=access_token, refresh_token=refresh_token
    )
