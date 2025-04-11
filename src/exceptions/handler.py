import logging
from datetime import datetime
from exceptions.definitions import TestException
from exceptions.schemas import ErrorResponse
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_error_response(message):
    now = datetime.now().isoformat()
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(message=message, timestamp=now).model_dump()
    )

# TODO Remove TestExeption
async def test_exception_handler(request: Request, exc: TestException) -> JSONResponse:
    """Handles ResourceNotFoundException."""
    logger.warning("Test Exception")
    return create_error_response(exc.message)

def register_exception_handlers(app: FastAPI) -> None:
    """Adds exception handlers to the FastAPI application."""
    app.add_exception_handler(TestException, test_exception_handler)