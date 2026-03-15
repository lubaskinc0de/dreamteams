from typing import ClassVar

from dreamteams.entities.errors import AppError, app_error


@app_error
class InvalidParticipantDataError(AppError):
    """Participant data is invalid."""

    message: str
    code: ClassVar[str] = "INVALID_PARTICIPANT_DATA"


@app_error
class ParticipantUserIdMismatchError(AppError):
    """The error occurs when an attempt is made to attach an participant to user B with a user id of user A."""

    message: str = "You're trying to attach an participant of user A to user B"
    code: ClassVar[str] = "PARTICIPANT_USER_ID_MISMATCH"
