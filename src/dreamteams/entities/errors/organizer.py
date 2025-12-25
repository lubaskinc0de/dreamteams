from typing import ClassVar

from dreamteams.entities.errors.base import AppError, app_error


@app_error
class UserAlreadyOrganizerError(AppError):
    """The error occurs when an attempt is made to create an organizer role for a user who is already an organizer."""

    code: ClassVar[str] = "USER_ALREADY_ORGANIZER"
    message: str = "User already has organizer role"


@app_error
class OrganizerUserIdMismatchError(AppError):
    """The error occurs when an attempt is made to attach an organizer to user B with a user id of user A."""

    code: ClassVar[str] = "ORGANIZER_USER_ID_MISMATCH"
    message: str = "You're trying to attach an organizer of user A to user B"
