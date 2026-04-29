from datetime import datetime
from typing import Any, ClassVar, override

from dreamteams.entities.common.identifiers import UserId
from dreamteams_common.errors import AppError, app_error


@app_error
class UserBlockedError(AppError):
    """Raised when a blocked user attempts to authenticate."""

    code: ClassVar[str] = "ACCOUNT_BLOCKED"
    message: str = "Your account has been blocked"
    reason: str | None = None
    blocked_at: datetime | None = None

    @override
    @property
    def meta(self) -> dict[str, Any] | None:
        return {
            "reason": self.reason,
            "blocked_at": self.blocked_at.isoformat() if self.blocked_at else None,
        }


@app_error
class InvalidSuperuserPasswordError(AppError):
    """Raised when the supplied password does not match the configured superuser hash."""

    code: ClassVar[str] = "INVALID_SUPERUSER_PASSWORD"
    message: str = "Invalid superuser password"


@app_error
class UserNotFoundError(AppError):
    """Error raised when attempting to access a user that does not exist in the system."""

    code: ClassVar[str] = "USER_NOT_FOUND"
    message: str = "User not found"
    user_id: UserId

    @override
    @property
    def meta(self) -> dict[str, Any] | None:
        return {
            "user_id": self.user_id,
        }
