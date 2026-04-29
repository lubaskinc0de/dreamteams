from enum import StrEnum, auto


class ApplicationStatus(StrEnum):
    """Status of a registration application — mirrors main's ApplicationStatus."""

    PENDING = auto()
    ACCEPTED = auto()
    REJECTED = auto()
