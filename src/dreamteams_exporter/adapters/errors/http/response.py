from typing import Any, ClassVar, override

from pydantic import BaseModel

from dreamteams_common.errors import AppError, app_error


class ErrorResponse(BaseModel):
    """Standard error payload returned by the exporter's internal HTTP API."""

    code: str
    message: str
    meta: dict[str, Any] | None


@app_error
class InternalServerError(AppError):
    """Fallback wrapper used when an unexpected exception."""

    code: ClassVar[str] = "INTERNAL_SERVER_ERROR"
    message: str = "Internal Server Error"
    orig_error: Exception


@app_error
class ValidationError(AppError):
    """Shape emitted when FastAPI raises ``RequestValidationError`` for malformed payloads."""

    code: ClassVar[str] = "VALIDATION_ERROR"
    message: str = "Validation error"
    details: dict[str, Any]

    @override
    @property
    def meta(self) -> dict[str, Any]:
        return self.details
