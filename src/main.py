from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.middleware import jwt_authentication_middleware
from src.exceptions.definitions import BaseAppException, InvalidJsonDataFormat
import src.models  # noqa: F401
from src.config.database import initialize_database
from exceptions.handler import base_app_exception_handler
from src.config.config import FRONTEND_URL

# Import routers
from auth.router import router as auth_router
from project.router import router as project_router
from user.router import router as user_router


app = FastAPI(
    title="Coordipai Web Server",
    description="",
    version="1.0.0",
)

initialize_database()
app.add_exception_handler(BaseAppException, base_app_exception_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(jwt_authentication_middleware)


@app.get("/", summary="Test API")
def read_root():
    return {"message": "Hello World"}


# Include routers
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(user_router)
