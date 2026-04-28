from enum import StrEnum, auto


class ParticipantType(StrEnum):
    """Target audience category for a competition."""

    SCHOOLCHILD = auto()
    STUDENT = auto()
    ANY = auto()
