from typing import ClassVar

from dreamteams.entities.errors.base import AppError, app_error


@app_error
class OrganizerUserIdMismatchError(AppError):
    """The error occurs when an attempt is made to attach an organizer to user B with a user id of user A."""

    code: ClassVar[str] = "ORGANIZER_USER_ID_MISMATCH"
    message: str = "You're trying to attach an organizer of user A to user B"
