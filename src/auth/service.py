from typing import Optional

from fastapi import Cookie, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth.schemas import AuthReq, AuthRes
from auth.util.github import get_github_access_token, get_github_user_info
from auth.util.jwt import create_access_token, create_refresh_token, parse_token
from auth.util.redis import (
    delete_token_from_redis,
    get_token_from_redis,
    save_token_to_redis,
)
from src.config.config import ACCESS_TOKEN_EXPIRE_MINUTES, FRONTEND_URL, IS_LOCAL
from src.response.error_definitions import (
    AccessTokenNotFound,
    GitHubAccessTokenError,
    GitHubCredentialCodeNotFound,
    InvalidRefreshToken,
    UserAlreadyExist,
    UserNotFound,
)
from src.user import repository as user_repository
from src.user import service as user_service
from src.user.schemas import UserReq, UserRes

GITHUB_OAUTH_REDIS = "github_oauth"
REFRESH_TOKEN_REDIS = "refresh_token"


async def github_callback(
    request: Request,
    db: Session,
):
    """
    Callback function for GitHub OAuth

    Returns resposne with access token
    """
    code = request.query_params.get("code")
    if not code:
        raise GitHubCredentialCodeNotFound()

    github_access_token = await get_github_access_token(code)
    if not github_access_token:
        raise GitHubAccessTokenError()

    github_user = await get_github_user_info(github_access_token)
    github_id = github_user["id"]
    github_name = github_user["login"]

    # Check if there is user data in db
    existing_user = user_repository.find_user_by_github_id(db, github_id)

    if existing_user:
        """
        Redirect to Login Page
        """
        access_token = create_access_token(github_id)
        redirect = RedirectResponse(url=f"{FRONTEND_URL}/")

        if IS_LOCAL:
            redirect.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                samesite="lax",
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES,
                path="/",
            )
        else:
            redirect.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="none",
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES,
                path="/",
            )
    else:
        """
        Redirect to Register Page
        """
        # Save GitHub AccessToken in redis temporary
        await save_token_to_redis(GITHUB_OAUTH_REDIS, github_id, github_access_token)
        access_token = create_access_token(github_id)

        redirect = RedirectResponse(url=f"{FRONTEND_URL}/register/{github_name}")

        if IS_LOCAL:
            redirect.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                samesite="lax",
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES,
                path="/",
            )
        else:
            redirect.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="none",
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES,
                path="/",
            )

    return redirect


async def register(
    db: Session, auth_req: AuthReq, access_token: Optional[str] = Cookie(None)
):
    """
    Register new user

    Returns user data and access & refresh token
    """
    if not access_token:
        raise AccessTokenNotFound()

    github_id = parse_token(access_token)
    github_access_token = await get_token_from_redis(GITHUB_OAUTH_REDIS, github_id)

    existing_user = user_repository.find_user_by_github_id(db, github_id)
    if existing_user:
        raise UserAlreadyExist()

    github_user = await get_github_user_info(github_access_token)

    new_user = UserReq(
        **auth_req.model_dump(),
        github_id=github_user["id"],
        github_name=github_user["login"],
        profile_img=github_user["avatar_url"],
    )
    saved_user = await user_service.create_user(db, new_user)
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


async def login(db: Session, access_token: Optional[str] = Cookie(None)):
    """
    Login existing user

    Returns user data and access & refresh token
    """
    if not access_token:
        raise AccessTokenNotFound()

    github_id = parse_token(access_token)
    github_access_token = await get_token_from_redis(GITHUB_OAUTH_REDIS, github_id)

    existing_user = user_repository.find_user_by_github_id(db, github_id)
    if not existing_user:
        raise UserNotFound()

    # Update github info
    user_service.update_github_user(db, github_id)

    # Delete github access token stored in redis
    await delete_token_from_redis(github_access_token)

    access_token = create_access_token(existing_user.id)
    refresh_token = create_refresh_token(existing_user.id)

    # Save refresh token in redis
    await save_token_to_redis(REFRESH_TOKEN_REDIS, existing_user.id, refresh_token)

    user_res = UserRes.model_validate(existing_user)
    print(access_token)

    return AuthRes(
        user=user_res, access_token=access_token, refresh_token=refresh_token
    )


async def refresh(db: Session, refresh_token: str):
    """
    Return new access & refresh token

    Validate existing refresh token and reissue new tokens
    """
    # redis compoare for validation
    user_id = parse_token(refresh_token)
    redis_refresh_token = await get_token_from_redis(REFRESH_TOKEN_REDIS, user_id)

    if refresh_token != redis_refresh_token:
        raise InvalidRefreshToken()

    user = user_repository.find_user_by_user_id(db, user_id)
    if not user:
        raise UserNotFound()

    # Delete existing refresh token stored in redis
    await delete_token_from_redis(refresh_token)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Save refresh token in redis
    await save_token_to_redis(REFRESH_TOKEN_REDIS, user.id, refresh_token)

    return AuthRes(user=user, access_token=access_token, refresh_token=refresh_token)


async def update(user_id: int, auth_req: AuthReq, db: Session):
    """
    Update user info

    Returns updated user data
    """
    user = user_repository.find_user_by_user_id(db, user_id)

    if not user:
        raise UserNotFound()

    github_user = await get_github_user_info(user.github_access_token)

    updating_user = UserReq(
        **auth_req.model_dump(),
        github_id=github_user["id"],
        github_name=github_user["login"],
        profile_img=github_user["avatar_url"],
    )
    updated_user = await user_service.update_user(db, updating_user)
    data = UserRes.model_validate(updated_user)

    return data


async def logout(user_id: int):
    """
    Logout user

    Deleting refresh token stored in redis
    """
    # Delete existing refresh token stored in redis
    redis_refresh_token = await get_token_from_redis(REFRESH_TOKEN_REDIS, user_id)
    await delete_token_from_redis(redis_refresh_token)
