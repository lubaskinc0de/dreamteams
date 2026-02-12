from typing import ClassVar

from dreamteams.entities.errors import AppError, app_error


@app_error
class InvalidParticipantContactError(AppError):
    """Participant contact data is invalid."""

    message: str
    code: str[ClassVar] = "INVALID_PARTICIPANT_CONTACT"


@app_error
class InvalidParticipantSkillError(AppError):
    """Participant skill data is invalid."""

    message: str
    code: str[ClassVar] = "INVALID_PARTICIPANT_SKILL"
