from typing import Any, ClassVar, override

from dreamteams.entities.errors.base import AppError, app_error


@app_error
class InvalidAvatarError(AppError):
    """Error is raised when uploaded file is not a valid avatar image."""

    reason: str
    message: str = "The uploaded file is not a valid image."
    code: ClassVar[str] = "INVALID_AVATAR_ERROR"

    @property
    @override
    def meta(self) -> dict[str, Any]:
        return {
            "reason": self.reason,
        }
