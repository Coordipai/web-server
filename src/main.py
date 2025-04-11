from fastapi import FastAPI
from exceptions.handler import register_exception_handlers
# TODO Remove TestExeption
from exceptions.definitions import TestException

from src.auth.router import router as auth_router


app = FastAPI(
    title="Coordipai Web Server",
    description="",
    version="1.0.0"
    )

register_exception_handlers(app)

app.include_router(auth_router)

@app.get("/", summary="Test API")
def read_root():
    return {"message": "Hello World"}

# TODO Remove TestExeption
@app.get("/oh-no")
def app_exception_handler():
    raise TestException("Oh no")