from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.config.middleware import jwt_authentification_middleware
from src.exceptions.definitions import BaseAppException
import src.models  # noqa: F401
from src.config.database import initialize_database
from exceptions.handler import register_exception_handlers
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

# Initialize Database and Global Exception Handler
initialize_database()
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def jwt_middleware(request: Request, call_next):
    return jwt_authentification_middleware(request, call_next)


@app.get("/", summary="Test API")
def read_root():
    return {"message": "Hello World"}


# Include routers
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(user_router)
