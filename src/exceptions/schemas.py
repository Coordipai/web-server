from pydantic import BaseModel
from datetime import datetime

class ErrorResponse(BaseModel):
    message: str
    timestamp: str
