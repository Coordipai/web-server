
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.auth.util.jwt import parse_token
from src.config.logger_config import add_daily_file_handler, setup_logger
from src.response.error_definitions import (
    BaseAppException,
    InvalidJwtToken,
    JwtTokenNotFound,
)
from src.response.schemas import ErrorResponse

logger = setup_logger(__name__)
add_daily_file_handler(logger)


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_allow_paths = [
            "/auth/github/login",
            "/auth/github/callback",
            "/auth/login",
            "/auth/register",
        ]
        api_docs_allow_paths = ["/docs", "/openapi.json"]

        if any(request.url.path.startswith(path) for path in auth_allow_paths):
            return await call_next(request)

        if any(request.url.path.startswith(path) for path in api_docs_allow_paths):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        try:
            # Extract Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise JwtTokenNotFound()

            access_token = auth_header[7:]  # Remove 'Bearer '

            try:
                user_id = parse_token(access_token)
                request.state.user_id = user_id
            except ValueError:
                raise InvalidJwtToken()

            response = await call_next(request)
            return response
        except BaseAppException as exc:
            logger.error(f"{exc.status_code} - {exc.message}")
            return JSONResponse(
                status_code=exc.status_code,
                headers={"Access-Control-Allow-Origin": "http://localhost:5173"},
                content=ErrorResponse(
                    method=request.method, path=request.url.path, message=exc.message
                ).model_dump(),
            )
