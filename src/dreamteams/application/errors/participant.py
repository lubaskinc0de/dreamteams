from typing import ClassVar

from dreamteams_common.errors import AppError, app_error


@app_error
class ParticipantNotFoundError(AppError):
    """The error occurs when a participant is not found."""

    code: ClassVar[str] = "PARTICIPANT_NOT_FOUND"
    message: str = "Participant not found"
