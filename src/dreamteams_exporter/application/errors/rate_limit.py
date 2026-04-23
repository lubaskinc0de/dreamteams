from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class RateLimitExceededError(AppError):
    """Raised when a user exceeds the export rate limit in the current window."""

    code: ClassVar[str] = "EXPORT_RATE_LIMIT_EXCEEDED"
    message: str = "Export rate limit exceeded"
