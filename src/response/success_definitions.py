from typing import TypeVar

from src.response.handler import success_handler


T = TypeVar("T")


def login_success(data: T):
    return success_handler(200, "로그인 성공", data)


def register_success(data: T):
    return success_handler(200, "회원가입 성공", data)


def refresh_token_success(data: T):
    return success_handler(200, "리프레시 토큰 재발급 성공", data)


def logout_success():
    return success_handler(200, "로그아웃 성공")
