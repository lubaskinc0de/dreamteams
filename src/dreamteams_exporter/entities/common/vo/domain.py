from enum import StrEnum, auto


class Domain(StrEnum):
    """IT domain area — mirrors main's Domain."""

    FRONTEND = auto()
    MOBILE = auto()
    BACKEND = auto()
    AI = auto()
    DEVOPS = auto()
