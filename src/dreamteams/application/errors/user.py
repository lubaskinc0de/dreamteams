from typing import Any, ClassVar, override

from dreamteams.entities.common.identifiers import UserId
from dreamteams.entities.errors.base import AppError, app_error


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
