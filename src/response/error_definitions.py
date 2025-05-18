class BaseAppException(Exception):
    def __init__(
        self,
        type: str = "about:blank",
        title: str = "Unknown Error",
        status_code: int = 500,
        detail: str | None = None,
    ):
        self.type = type
        self.title = title
        self.status_code = status_code
        self.detail = detail or ""
        super().__init__(self.title)


"""
400 BAD_REQUEST
"""


class BadRequestException(BaseAppException):
    def __init__(self, title: str, detail: str | None = None):
        super().__init__(title=title, status_code=400, detail=detail)


class InvalidJsonFormat(BadRequestException):
    def __init__(self):
        super().__init__(
            title="JSON 파싱 오류",
            detail="요청 본문은 올바른 JSON 형식이어야 합니다.",
        )


class InvalidJsonDataFormat(BadRequestException):
    def __init__(self, missing_fields: list[str] | None = None):
        base_detail = (
            "요청 본문은 아래 필드를 포함해야 하며, 형식도 올바른지 확인해 주세요:\n"
            "- `name`: 프로젝트 이름 (string)\n"
            "- `repo_fullname`: GitHub 저장소 전체 이름 (string)\n"
            "- `start_date` / `end_date`: ISO 8601 형식의 날짜 문자열 (예: '2024-01-01T00:00:00Z')\n"
            "- `sprint_unit`: 스프린트 단위 (int)\n"
            "- `discord_channel_id`: Discord 채널 ID (string)\n"
            "- `members`: 프로젝트 구성원 목록 (List[ProjectUserReq])\n"
            "- `design_docs`: 설계 문서 URL 목록 (List[str], 선택사항)"
        )

        if missing_fields:
            formatted = ", ".join(f"`{field}`" for field in missing_fields)
            base_detail += f"\n\n요청에서 누락된 필드: {formatted}"

        super().__init__(
            title="JSON 데이터 형식 오류",
            detail=base_detail,
        )


class InvalidPriority(BadRequestException):
    def __init__(self, priority):
        super().__init__(
            title="잘못된 요청 형식",
            detail=f"우선순위 값은 M, S, C, W 중 하나입니다. (요청 값: {priority})",
        )


class InvalidReschedulingType(BadRequestException):
    def __init__(self, type):
        super().__init__(
            title="잘못된 요청 형식",
            detail=f"이슈 변경 요청서 결과 값은 Approve, Disapprove 중 하나입니다. (요청 값: {type})",
        )


"""
401 UNAUTHORIZED
"""


class UnauthorizedException(BaseAppException):
    def __init__(self, title: str, detail: str | None = None):
        super().__init__(title=title, status_code=401, detail=detail)


class JwtTokenNotFound(UnauthorizedException):
    def __init__(self):
        super().__init__(
            title="인증 토큰 누락",
            detail="Authorization 헤더가 누락되었거나, 'Bearer <token>' 형식이 아닙니다.",
        )


class InvalidJwtToken(UnauthorizedException):
    def __init__(self, reason: str | None = None):
        detail = "JWT 토큰이 유효하지 않습니다."
        if reason:
            detail += f" 상세 사유: {reason}"
        super().__init__(title="유효하지 않은 토큰", detail=detail)


class ExpiredJwtToken(UnauthorizedException):
    def __init__(self):
        super().__init__(
            title="만료된 토큰",
            detail="JWT 토큰이 만료되었습니다. 토큰을 새로 발급받아야 합니다.",
        )


class InvalidRefreshToken(UnauthorizedException):
    def __init__(self):
        super().__init__(
            title="유효하지 않은 토큰", detail="RefreshToken이 유효하지 않습니다."
        )


class ProjectOwnerMismatched(UnauthorizedException):
    def __init__(self):
        super().__init__(
            title="프로젝트 소유권 불일치",
            detail="프로젝트 삭제는 소유자만 할 수 있습니다. 현재 사용자는 프로젝트 소유자가 아닙니다.",
        )


"""
404 NOT_FOUND
"""


class NotFoundException(BaseAppException):
    def __init__(self, title: str, detail: str | None = None):
        super().__init__(title=title, status_code=404, detail=detail)


class GitHubCredentialCodeNotFound(NotFoundException):
    def __init__(self):
        super().__init__(
            title="인증 정보 누락", detail="GitHub 인가 코드를 찾을 수 없습니다."
        )


class AccessTokenNotFound(NotFoundException):
    def __init__(self):
        super().__init__(
            title="인증 정보 누락", detail="쿠키에서 AccessToken을 찾을 수 없습니다."
        )


class UserNotFound(NotFoundException):
    def __init__(self):
        super().__init__(
            title="사용자를 찾을 수 없음",
            detail="요청하신 사용자 정보를 찾을 수 없습니다.",
        )


class ProjectNotFound(NotFoundException):
    def __init__(self):
        super().__init__(
            title="프로젝트를 찾을 수 없음",
            detail="요청하신 프로젝트 ID에 해당하는 프로젝트가 존재하지 않습니다.",
        )


class IssueReschedulingNotFound(NotFoundException):
    def __init__(self):
        super().__init__(
            title="이슈 변경 요청서 없음",
            detail="요청하신 이슈 변경 요청서 정보를 찾을 수 없습니다.",
        )


class IssueNotFound(NotFoundException):
    def __init__(self):
        super().__init__(
            title="이슈 없음", detail="요청하신 이슈 정보를 찾을 수 없습니다."
        )


class DesignDocNotFound(NotFoundException):
    def __init__(self):
        super().__init__(
            title="설계 문서 없음", detail="요청하신 설계 문서 정보를 찾을 수 없습니다."
        )


class RepositoryNotFoundInGitHub(NotFoundException):
    def __init__(self, repo_fullname: str):
        super().__init__(
            title="GitHub 레포지토리 없음",
            detail=f"GitHub에서 '{repo_fullname}' 레포지토리를 찾을 수 없습니다. 올바른 레포지토리 이름인지 확인해주세요.",
        )


"""
405 METHOD_NOT_ALLOWED
"""


class MethodNotAllowedException(BaseAppException):
    def __init__(self, title: str, detail: str | None = None):
        super().__init__(title=title, status_code=405, detail=detail)


"""
409 CONFLICT
"""


class ConflictException(BaseAppException):
    def __init__(self, title: str, detail: str | None = None):
        super().__init__(title=title, status_code=409, detail=detail)


class UserAlreadyExist(ConflictException):
    def __init__(self):
        super().__init__(
            title="사용자 정보 중복",
            detail="이미 등록된 사용자 정보가 있습니다. 다른 정보로 시도하거나 로그인해 주세요.",
        )


class ProjectAlreadyExist(ConflictException):
    def __init__(self):
        super().__init__(
            title="프로젝트 정보 중복",
            detail="이미 같은 이름이나 조건의 프로젝트가 등록되어 있습니다. 다른 프로젝트 이름을 사용해 주세요.",
        )


class IssueReschedulingAlreadyExist(ConflictException):
    def __init__(self):
        super().__init__(
            title="이슈 변경 요청서 중복",
            detail="해당 이슈에 대한 변경 요청서가 이미 존재합니다. 기존 요청서를 확인해 주세요.",
        )


"""
415 UNSUPPORTED_MEDIA_TYPE
"""


class UnsupportedMediaType(BaseAppException):
    def __init__(self, title: str, detail: str | None = None):
        super().__init__(title=title, status_code=415, detail=detail)


class InvalidFileType(UnsupportedMediaType):
    def __init__(self):
        super().__init__(
            title="지원하지 않는 파일 형식",
            detail="업로드한 파일 형식이 시스템에서 지원하지 않는 형식입니다. 허용된 파일 형식을 확인해 주세요.",
        )


"""
500 INTERNAL_SERVER_ERROR
"""


class InternalServerErrorException(BaseAppException):
    def __init__(self, title: str, detail: str | None = None):
        super().__init__(title=title, status_code=500, detail=detail)


class GitHubAccessTokenError(InternalServerErrorException):
    def __init__(self):
        super().__init__(
            title="GitHub AccessToken 오류",
            detail="GitHub에서 AccessToken을 정상적으로 받아오지 못했습니다. 네트워크 상태나 GitHub OAuth 설정을 확인해 주세요.",
        )


class SQLError(InternalServerErrorException):
    def __init__(self):
        super().__init__(
            title="데이터베이스 오류",
            detail="요청을 처리하는 중 데이터베이스에서 문제가 발생했습니다. 관리자에게 문의해 주세요.",
        )


class GitHubApiError(InternalServerErrorException):
    def __init__(self, status_code: int, detail: str | None = None):
        error_detail = f"GitHub API 요청 처리 중 문제가 발생했습니다. (응답 상태 코드: {status_code})"
        if detail:
            error_detail += f" 세부 내용: {detail}"
        super().__init__(
            title="GitHub API 오류",
            detail=error_detail,
        )


class GitHubActivationInfoError(InternalServerErrorException):
    def __init__(self):
        super().__init__(
            title="GitHub Activation Info 오류",
            detail="GitHub API로부터 활성화 정보를 정상적으로 받아오지 못했습니다. 네트워크 상태와 API 권한 설정을 확인해 주세요.",
        )


class FileDeleteError(InternalServerErrorException):
    def __init__(self):
        super().__init__(
            title="파일 삭제 오류",
            detail="서버 내 파일 삭제 작업 도중 오류가 발생했습니다. 파일 경로나 권한 문제를 점검해 주세요.",
        )


class IssueGenerateError(InternalServerErrorException):
    def __init__(self):
        super().__init__(
            title="이슈 생성 오류",
            detail="이슈를 생성하는 중 문제가 발생했습니다. 관리자에게 문의해 주세요.",
        )

class LLMResponseFormatError(InternalServerErrorException):
    def __init__(self):
        super().__init__(
            title="LLM 응답 형식 오류",
            detail="LLM의 응답 형식이 잘못되었습니다.",
        )
