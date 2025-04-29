from starlette.requests import Request
from src.auth.util.jwt import parse_token
from src.exceptions.definitions import InvalidJwtToken, JwtTokenNotFound


async def jwt_authentification_middleware(self, request: Request, call_next):
    # Allow paths
    open_paths = ["/auth/login", "/auth/register"]

    if any(request.url.path.startswith(path) for path in open_paths):
        return await call_next(request)

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
