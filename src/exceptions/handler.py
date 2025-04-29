from datetime import datetime
from exceptions.schemas import ErrorResponse
from exceptions.definitions import BaseAppException
from fastapi import Request
from fastapi.responses import JSONResponse
from src.config.logger_config import setup_logger, add_daily_file_handler


logger = setup_logger(__name__)
add_daily_file_handler(logger)


async def base_app_exception_handler(
    request: Request, exc: BaseAppException
) -> JSONResponse:
    now = datetime.now().isoformat()
    logger.error(f"{exc.status_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=exc.message, timestamp=now).model_dump(),
    )
