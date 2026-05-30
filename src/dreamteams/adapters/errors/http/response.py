from typing import Any, ClassVar, override

from pydantic import BaseModel

from dreamteams_common.errors import AppError, app_error


class ErrorResponse(BaseModel):
    """Standard error response model returned to API clients."""

    code: str
    message: str
    meta: dict[str, Any] | None


@app_error
class InternalServerError(AppError):
    """Generic error used as fallback when an unexpected exception occurs."""

    code: ClassVar[str] = "INTERNAL_SERVER_ERROR"
    message: str = "Internal Server Error"
    orig_error: Exception


@app_error
class IntegrityConflictError(AppError):
    """Generic error used when a database integrity constraint rejects a write."""

    code: ClassVar[str] = "INTEGRITY_CONFLICT"
    message: str = "Integrity constraint violated"
    orig_error: Exception


@app_error
class ValidationError(AppError):
    """Error used as when fastapi ``RequestValidationError`` exception occurs."""

    code: ClassVar[str] = "VALIDATION_ERROR"
    message: str = "Validation error"
    details: dict[str, Any]

    @override
    @property
    def meta(self) -> dict[str, Any]:
        return self.details
