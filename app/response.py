from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    error: str | None = None
    data: Any = None
