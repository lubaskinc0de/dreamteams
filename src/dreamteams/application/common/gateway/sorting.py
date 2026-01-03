from enum import StrEnum, auto


class SortOrder(StrEnum):
    """Sort order for listing operations."""

    ASC = auto()
    DESC = auto()
