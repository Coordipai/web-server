import traceback
import uuid

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.auth.util.jwt import parse_token
from src.config.config import DISCORD_CHANNEL_ID
from src.config.logger_config import add_daily_file_handler, setup_logger
from src.config.trace_config import set_trace_id
from src.response.error_definitions import (
    BaseAppException,
    InvalidJwtToken,
    JwtTokenNotFound,
)
from src.response.report_error import report_error_to_discord
from src.response.schemas import ErrorResponse

logger = setup_logger(__name__)
add_daily_file_handler(logger)


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())
        set_trace_id(trace_id)

        auth_allow_paths = [
            "/auth/github/login",
            "/auth/github/callback",
            "/auth/login",
            "/auth/register",
            "/auth/refresh",
        ]
        api_docs_allow_paths = ["/docs", "/openapi.json"]
        discord_bot_allow_paths = ["/bot"]

        if any(request.url.path.startswith(path) for path in auth_allow_paths):
            response = await call_next(request)
            response.headers["Trace-ID"] = trace_id
            return response

        if any(request.url.path.startswith(path) for path in api_docs_allow_paths):
            response = await call_next(request)
            response.headers["Trace-ID"] = trace_id
            return response

        if request.method == "OPTIONS":
            response = await call_next(request)
            response.headers["Trace-ID"] = trace_id
            return response

        is_discord_bot = request.headers.get("Discord-Bot") == "true"
        if is_discord_bot and any(
            request.url.path.startswith(path) for path in discord_bot_allow_paths
        ):
            response = await call_next(request)
            response.headers["Trace-ID"] = trace_id
            return response

        try:
            # Extract Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise JwtTokenNotFound()

            access_token = auth_header[7:]  # Remove 'Bearer '

            try:
                user_id = parse_token(access_token)
                request.state.user_id = user_id
            except ValueError as e:
                raise InvalidJwtToken(reason=str(e))

            response = await call_next(request)
            response.headers["Trace-ID"] = trace_id
            return response
        except BaseAppException as exc:
            type = exc.type
            title = exc.title
            status_code = exc.status_code
            path = request.url.path
            detail = exc.detail
            method = request.method
            stack_trace = traceback.format_exc()

            logger.error(f"{exc.status_code} - {exc.title}")

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

            response = JSONResponse(
                status_code=status_code,
                headers={"Access-Control-Allow-Origin": "http://localhost:5173"},
                content=ErrorResponse(
                    method=method,
                    path=path,
                    title=title,
                    detail=detail,
                ).model_dump(),
            )
            response.headers["Trace-ID"] = trace_id
            return response
