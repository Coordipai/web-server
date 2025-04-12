import exceptions.definitions as definitions
from fastapi import APIRouter, Request
from src.auth import service, schemas

router = APIRouter(prefix="/auth", tags=["GitHub OAuth"])


@router.get("/login", summary="Redirect to GitHub login page")
def login_with_github():
    return service.login_with_github()


@router.get(
    "/github/callback",
    response_model=schemas.GitHubUser,
    summary="Callback for GitHub login",
)
async def github_callback(request: Request):
    return await service.github_callback(request)


@router.post("/update", response_model=schemas.User, summary="Create/Update user")
async def create_or_update_user():
    return await service.create_or_update_user()
