from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from auth.util.jwt import create_access_token
from auth.util.redis import save_token_to_redis
from auth.util.github import get_github_access_token, get_github_user_info
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, FRONTEND_URL


async def github_callback(request: Request, response: Response):
    """
    Callback function for GitHub OAuth

    Returns resposne with access token
    """
    code = request.query_params.get("code")
    if not code:
        # TODO Use Custom Exceptions
        return {"error": "No code provided"}

    github_access_token = await get_github_access_token(code)
    if not github_access_token:
        # TODO Use Custom Exceptions
        return {"error": "Failed to get access token"}

    github_user = await get_github_user_info(github_access_token)
    github_id = github_user["id"]

    # Save GitHub AccessToken in redis before register
    save_token_to_redis("github_oauth", github_id, github_access_token)

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
