import httpx

from src.config.config import (
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_REDIRECT_URI,
)

GITHUB_OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_USER_URL = "https://api.github.com/user"


async def get_github_access_token(code: str) -> str | None:
    """
    Get GitHub AccessToken
    """
    async with httpx.AsyncClient() as client:
        headers = {"Accept": "application/json"}
        data = {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": GITHUB_REDIRECT_URI,
        }

        res = await client.post(
            GITHUB_OAUTH_ACCESS_TOKEN_URL, headers=headers, data=data
        )
        return res.json().get("access_token")


async def get_github_user_info(access_token: str) -> dict:
    """
    Get GitHub User Info
    """
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}

        res = await client.get(GITHUB_API_USER_URL, headers=headers)
        return res.json()
