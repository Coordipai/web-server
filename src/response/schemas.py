from datetime import datetime
from typing import Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    method: str
    path: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SuccessContent(BaseModel, Generic[T]):
    message: str
    data: Optional[Union[T, List[T]]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SuccessResponse(BaseModel, Generic[T]):
    status_code: int
    content: SuccessContent[T]
