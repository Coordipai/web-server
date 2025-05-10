import secrets

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
from src.config.config import FRONTEND_URL, SWAGGER_PASSWORD, SWAGGER_USERNAME
from src.config.database import initialize_database
from src.config.middleware import jwt_authentication_middleware
from src.response.error_definitions import BaseAppException
from src.response.handler import exception_handler
from user.router import router as user_router
from user_repository.router import router as user_repository_router

app = FastAPI(
    title="Coordipai Web Server",
    description="",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

initialize_database()
app.add_exception_handler(BaseAppException, exception_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(jwt_authentication_middleware)

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
