from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import Base, engine
from exceptions.handler import register_exception_handlers
from src.config import FRONTEND_URL

# Import routers
from auth.router import router as auth_router

# TODO Remove TestExeption
from exceptions.definitions import TestException

app = FastAPI(title="Coordipai Web Server", description="", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Database
Base.metadata.create_all(bind=engine)

# Register Global Exception Handler
register_exception_handlers(app)

# Include routers
app.include_router(auth_router)


@app.get("/", summary="Test API")
def read_root():
    return {"message": "Hello World"}


# TODO Remove TestExeption
@app.get("/oh-no")
def app_exception_handler():
    raise TestException("Oh no")
