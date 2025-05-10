from datetime import datetime
from typing import Optional, TypeVar

from fastapi import Request
from fastapi.responses import JSONResponse

from src.config.logger_config import add_daily_file_handler, setup_logger
from src.response.error_definitions import BaseAppException
from src.response.schemas import ErrorResponse, SuccessContent, SuccessResponse

logger = setup_logger(__name__)
add_daily_file_handler(logger)

T = TypeVar("T")


async def exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    logger.error(f"{exc.status_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=exc.message).model_dump(),
    )


def success_handler(status_code: int, message: str, data: Optional[T] = None):
    return SuccessResponse(
        status_code=status_code, content=SuccessContent(message=message, data=data)
    )
