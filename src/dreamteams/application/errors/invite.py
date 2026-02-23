from typing import ClassVar

from dreamteams.entities.errors.base import AppError, app_error


@app_error
class InviteNotFoundError(AppError):
    """Raised when an organizer invite is not found by code or ID."""

    code: ClassVar[str] = "INVITE_NOT_FOUND"
    message: str = "Invite not found"
