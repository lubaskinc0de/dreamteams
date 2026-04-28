from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class AccessDeniedError(AppError):
    """Error raised when a user attempts to access a resource they don't have permission for."""

    code: ClassVar[str] = "ACCESS_DENIED"
    message: str = "Access denied"
