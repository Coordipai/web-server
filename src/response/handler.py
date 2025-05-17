import traceback
from typing import Optional, TypeVar

from fastapi import Request
from fastapi.responses import JSONResponse

from src.config.config import DISCORD_CHANNEL_ID
from src.config.logger_config import add_daily_file_handler, setup_logger
from src.config.trace_config import get_trace_id
from src.response.error_definitions import BaseAppException
from src.response.report_error import report_error_to_discord
from src.response.schemas import ErrorResponse, SuccessContent, SuccessResponse

logger = setup_logger(__name__)
add_daily_file_handler(logger)

T = TypeVar("T")


async def exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    trace_id = get_trace_id()
    type = exc.type
    title = exc.title
    status_code = exc.status_code
    path = request.url.path
    detail = exc.detail
    method = request.method
    stack_trace = traceback.format_exc()

    logger.error(f"{status_code} - {title} - {detail}")

    if status_code >= 500:
        await report_error_to_discord(
            discord_channel_id=DISCORD_CHANNEL_ID,
            trace_id=trace_id,
            type=type,
            title=title,
            status=status_code,
            detail=detail,
            instance=path,
            method=method,
            trace=stack_trace,
        )

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            method=method, path=path, title=title, detail=detail
        ).model_dump(),
    )


def success_handler(status_code: int, message: str, data: Optional[T] = None):
    return SuccessResponse(
        status_code=status_code, content=SuccessContent(message=message, data=data)
    )
