from pydantic import BaseModel


from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")


class ErrorResponse(BaseModel):
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SuccessContent(BaseModel, Generic[T]):
    message: str
    data: Optional[T] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SuccessResponse(BaseModel, Generic[T]):
    status_code: int
    content: SuccessContent[T]
