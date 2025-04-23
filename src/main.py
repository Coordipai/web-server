from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.models  # noqa: F401
from src.database import initialize_database
from exceptions.handler import register_exception_handlers
from src.config import FRONTEND_URL

# Import routers
from auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Coordipai Web Server",
    description="",
    version="1.0.0",
    lifespan=lifespan,
)


# Register Global Exception Handler
register_exception_handlers(app)

# Include routers
app.include_router(auth_router)


@app.get("/", summary="Test API")
def read_root():
    return {"message": "Hello World"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
