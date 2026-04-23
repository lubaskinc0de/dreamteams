from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class InvalidRoleError(AppError):
    """Raised when a user attempts an operation their role is not permitted to perform."""

    code: ClassVar[str] = "INVALID_ROLE"
    message: str = "User role is not permitted to perform this action"
