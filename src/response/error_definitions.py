class BaseAppException(Exception):
    """Base exception for our application"""

    def __init__(self, message: str = "Unknown Error", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


"""
400 BAD_REQUEST
"""


class BadRequestException(BaseAppException):
    def __init__(self, message):
        super().__init__(message, 400)


class InvalidJsonFormat(BadRequestException):
    def __init__(self):
        super().__init__("Json format이 유효하지 않습니다.")


class InvalidJsonDataFormat(BadRequestException):
    def __init__(self):
        super().__init__("Json data format이 유효하지 않습니다.")


class InvalidReqFormat(BadRequestException):
    def __init__(self):
        super().__init__("요청 형식이 맞지 않습니다.")


"""
401 UNAUTHORIZED
"""


class UnauthorizedException(BaseAppException):
    def __init__(self, message):
        super().__init__(message, 401)


class JwtTokenNotFound(UnauthorizedException):
    def __init__(self):
        super().__init__("인증 정보를 찾을 수 없습니다.")


class InvalidJwtToken(UnauthorizedException):
    def __init__(self):
        super().__init__("유효하지 않은 토큰입니다.")


class ExpiredJwtToken(UnauthorizedException):
    def __init__(self):
        super().__init__("만료된 토큰입니다.")


class InvalidRefreshToken(UnauthorizedException):
    def __init__(self):
        super().__init__("RefreshToken이 유효하지 않습니다.")


class AccessTokenNotFound(UnauthorizedException):
    def __init__(self):
        super().__init__("AccessToken을 찾을 수 없습니다.")


class ProjectOwnerMismatched(UnauthorizedException):
    def __init__(self):
        super().__init__("프로젝트 소유권자만 프로젝트를 삭제시킬 수 있습니다.")


"""
404 NOT_FOUND
"""


class NotFoundException(BaseAppException):
    def __init__(self, message):
        super().__init__(message, 404)


class GitHubCredentialCodeNotFound(NotFoundException):
    def __init__(self):
        super().__init__("GitHub 인가 코드를 찾을 수 없습니다.")


class UserNotFound(NotFoundException):
    def __init__(self):
        super().__init__("사용자 정보를 찾을 수 없습니다.")


class ProjectNotFound(NotFoundException):
    def __init__(self):
        super().__init__("프로젝트 정보를 찾을 수 없습니다.")


class IssueReschedulingNotFound(NotFoundException):
    def __init__(self):
        super().__init__("이슈 변경 요청서 정보를 찾을 수 없습니다.")


class IssueNotFound(NotFoundException):
    def __init__(self):
        super().__init__("이슈 정보를 찾을 수 없습니다.")


"""
405 METHOD_NOT_ALLOWED
"""


class MethodNotAllowedException(BaseAppException):
    def __init__(self, message):
        super().__init__(message, 405)


"""
409 CONFLICT
"""


class ConflictException(BaseAppException):
    def __init__(self, message):
        super().__init__(message, 409)


class UserAlreadyExist(ConflictException):
    def __init__(self):
        super().__init__("사용자 정보가 이미 존재합니다.")


class ProjectAlreadyExist(ConflictException):
    def __init__(self):
        super().__init__("프로젝트 정보가 이미 존재합니다.")


class IssueReschedulingAlreadyExist(ConflictException):
    def __init__(self):
        super().__init__("이슈 변경 요청서가 이미 존재합니다.")


"""
415 UNSUPPORTED_MEDIA_TYPE
"""


class UnsupportedMediaType(BaseAppException):
    def __init__(self, message):
        super().__init__(message, 415)


class InvalidFileType(UnsupportedMediaType):
    def __init__(self):
        super().__init__("지원하지 않는 파일 형식입니다.")


"""
500 INTERNAL_SERVER_ERROR
"""


class InternalServerErrorException(BaseAppException):
    def __init__(self, message):
        super().__init__(message, 500)


class GitHubAccessTokenError(InternalServerErrorException):
    def __init__(self):
        super().__init__("GitHub AccessToken을 가져오는 중에 문제가 발생했습니다.")


class SQLError(InternalServerErrorException):
    def __init__(self):
        super().__init__("DB 관련 로직 처리 중 문제가 발생했습니다.")


class GitHubApiError(InternalServerErrorException):
    def __init__(self, code):
        super().__init__(
            f"GitHub 요청 처리 중 문제가 발생했습니다. (response status: {code})"
        )


class GitHubActivationInfoError(InternalServerErrorException):
    def __init__(self):
        super().__init__("GitHub Activation Info를 가져오는 중에 문제가 발생했습니다.")


class FileDeleteError(InternalServerErrorException):
    def __init__(self):
        super().__init__("파일 삭제 중 문제가 발생했습니다.")
