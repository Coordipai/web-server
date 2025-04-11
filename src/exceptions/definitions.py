class BaseAppException(Exception):
    """Base exception for our application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# TODO Remove TestExeption
class TestException(BaseAppException):
    """Raised when a requested resource is not found"""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)
