import httpx
from src.auth import config

GITHUB_OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_USER_URL = "https://api.github.com/user"
GITHUB_API_REPO_URL = "https://api.github.com/user/repos"

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
            }
        )
        return res.json().get("access_token")

async def get_github_user(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            GITHUB_API_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return res.json()

async def get_user_repos(access_token: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            GITHUB_API_REPO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"visibility": "all"}  # public + private repos
        )
        return res.json()
