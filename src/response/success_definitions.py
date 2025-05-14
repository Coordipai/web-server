from typing import TypeVar

from src.response.handler import success_handler

T = TypeVar("T")

"""
Auth Success Responses
"""


def login_success(data: T):
    return success_handler(200, "로그인 성공", data)


def register_success(data: T):
    return success_handler(201, "회원가입 성공", data)


def refresh_token_success(data: T):
    return success_handler(200, "리프레시 토큰 재발급 성공", data)


def user_update_success(data: T):
    return success_handler(200, "사용자 정보 업데이트 성공", data)


def logout_success():
    return success_handler(200, "로그아웃 성공")


def unregister_success():
    return success_handler(200, "탈퇴 성공")


"""
Project Success Responses
"""


def project_create_success(data: T):
    return success_handler(201, "프로젝트 생성 성공", data)


def project_read_success(data: T):
    return success_handler(200, "프로젝트 조회 성공", data)


def project_update_success(data: T):
    return success_handler(200, "프로젝트 수정 성공", data)


def project_delete_success():
    return success_handler(200, "프로젝트 삭제 성공")


"""
User Success Response
"""


def user_search_success(data: T):
    return success_handler(200, "사용자 조회 성공", data)


"""
Agent Success Response
"""


def issue_generate_success(data: T):
    return success_handler(200, "이슈 생성 성공", data)


def assess_success(data: T):
    return success_handler(200, "역량 평가 성공", data)


def assessment_read_success(data: T):
    return success_handler(200, "역량 조회 성공", data)


def issue_assign_success(data: T):
    return success_handler(200, "이슈 할당 성공", data)


"""
Issue Success Response
"""


def issue_create_success(data: T):
    return success_handler(201, "이슈 생성 성공", data)


def issue_read_success(data: T):
    return success_handler(200, "이슈 조회 성공", data)


def issue_update_success(data: T):
    return success_handler(200, "이슈 수정 성공", data)


def issue_close_success():
    return success_handler(200, "이슈 닫기 성공")


"""
Issue Rescheduling Request Success Response
"""


def issue_rescheduling_create_success(data: T):
    return success_handler(201, "이슈 변경 요청서 생성 성공", data)


def issue_rescheduling_read_success(data: T):
    return success_handler(200, "이슈 변경 요청서 조회 성공", data)


def issue_rescheduling_update_success(data: T):
    return success_handler(200, "이슈 변경 요청서 수정 성공", data)


def issue_rescheduling_delete_success():
    return success_handler(200, "이슈 변경 요청서 삭제 성공")


"""
User Repository Success Response
"""


def user_repository_sync_success(data: T):
    return success_handler(200, "역량 평가용 레포지토리 업데이트 성공", data)


def user_repository_read_success(data: T):
    return success_handler(200, "역량 평가용 레포지토리 조회 성공", data)


def user_repository_from_github_read_success(data: T):
    return success_handler(200, "GitHub 레포지토리 조회 성공", data)
