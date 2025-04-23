import logging
from datetime import datetime
from exceptions.definitions import *
from exceptions.schemas import ErrorResponse
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def base_app_exception_handler(
    request: Request, exc: BaseAppException
) -> JSONResponse:
    now = datetime.now().isoformat()
    logger.warning(f"{exc.status_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=exc.message, timestamp=now).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BaseAppException, base_app_exception_handler)
