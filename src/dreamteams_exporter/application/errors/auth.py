from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class UnauthorizedError(AppError):
    """Raised when the request has no resolvable caller identity."""

    code: ClassVar[str] = "UNAUTHORIZED"
    message: str = "Unauthorized"
