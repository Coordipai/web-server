import secrets
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import src.models  # noqa: F401
from agent.router import router as agent_router
from auth.router import router as auth_router
from issue.router import router as issue_router
from issue_rescheduling.router import router as issue_rescheduling_router
from project.router import router as project_router
from src.config.config import (
    DISCORD_CHANNEL_ID,
    FRONTEND_URL,
    IS_LOCAL,
    SWAGGER_PASSWORD,
    SWAGGER_USERNAME,
)
from src.config.database import initialize_database
from src.config.logger_config import setup_logger
from src.config.middleware import JWTAuthenticationMiddleware
from src.response.error_definitions import BaseAppException
from src.response.handler import base_app_exception_handler, global_exception_handler
from user.router import router as user_router
from user_repository.router import router as user_repository_router

logger = setup_logger(__name__)


async def send_server_info(status: str):
    if IS_LOCAL:
        return

    message = ""
    if status == "start":
        message = "The server is now online."
    elif status == "stop":
        message = "The server is shutting down."
    else:
        print("Unknown status")
        return

    url = "https://errorping.jhssong.com/info"
    payload = {
        "discordChannelId": DISCORD_CHANNEL_ID,
        "info": {"message": message},
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload)

        if res.status_code != 200:
            print(f"Failed to report error: {res.status_code} - {res.text}")
        logger.info(f"✅ {message}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # When server started
    await send_server_info("start")

    yield

    # When server stopped
    await send_server_info("stop")


app = FastAPI(
    title="Coordipai Web Server",
    description="",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

initialize_database()

app.add_exception_handler(BaseAppException, base_app_exception_handler)
# Should be lower than any other exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(JWTAuthenticationMiddleware)

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, SWAGGER_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, SWAGGER_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@app.get("/docs", include_in_schema=False)
async def get_documentation(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Secure API Docs")


# Include routers
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(user_router)
app.include_router(agent_router)
app.include_router(issue_router)
app.include_router(user_repository_router)
app.include_router(issue_rescheduling_router)
