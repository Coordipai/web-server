from typing import Optional
import httpx
from fastapi import Request
from fastapi.responses import RedirectResponse
from src.auth import config
from sqlalchemy.orm import Session
from src.auth.models import User
from src.auth import schemas


GITHUB_OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_USER_URL = "https://api.github.com/user"
GITHUB_API_REPO_URL = "https://api.github.com/user/repos"


def login_with_github():
    github_url = (
        f"{GITHUB_OAUTH_AUTHORIZE_URL}"
        f"?client_id={config.GITHUB_CLIENT_ID}"
        f"&redirect_uri={config.REDIRECT_URI}"
        "&scope=repo user"
    )
    return RedirectResponse(github_url, status_code=302)


async def exchange_code_for_token(code: str) -> str | None:
    async with httpx.AsyncClient() as client:
        res = await client.post(
            GITHUB_OAUTH_ACCESS_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": config.GITHUB_CLIENT_ID,
                "client_secret": config.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": config.REDIRECT_URI,
            },
        )
        return res.json().get("access_token")


async def github_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No code provided"}

    access_token = await exchange_code_for_token(code)
    if not access_token:
        return {"error": "Failed to get access token"}

    user = await get_github_user(access_token)

    return schemas.GitHubUser.model_validate(user)


async def get_github_user(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            GITHUB_API_USER_URL, headers={"Authorization": f"Bearer {access_token}"}
        )
        return res.json()


async def get_user_by_github(db: Session, access_token: str) -> Optional[User]:
    github_user = await get_github_user(access_token=access_token)
    user = db.query(User).filter(User.github_id == github_user["id"]).first()

    if user:
        user.github_access_token = access_token
        db.commit()
        db.refresh(user)
    return user


async def create_or_update_user(
    db: Session,
    access_token: str,
    discord_id: int,
    name: str,
    category: str,
    career: str,
) -> User:
    github_user = await get_github_user(access_token=access_token)
    user = db.query(User).filter(User.github_id == github_user["id"]).first()

    if user:
        user.name = name
        user.email = github_user["email"]
        user.discord_id = discord_id
        user.github_name = github_user["login"]
        user.category = category
        user.career = career
        user.github_access_token = access_token
    else:
        user = User(
            name=name,
            email=github_user["email"],
            discord_id=discord_id,
            github_id=github_user["id"],
            github_name=github_user["login"],
            github_access_token=access_token,
            category=category,
            career=career,
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return schemas.User.model_validate(user)
