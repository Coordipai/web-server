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


def logout_success():
    return success_handler(200, "로그아웃 성공")


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
