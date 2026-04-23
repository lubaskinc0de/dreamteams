from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Self

from dreamteams_exporter.entities.errors.job import InvalidJobStatusError


class JobStatusKind(StrEnum):
    """Discriminator for the JobStatus value object."""

    PENDING = auto()
    SUCCESS = auto()
    FAILED = auto()


@dataclass(frozen=True, slots=True, kw_only=True)
class JobStatus:
    """Value object describing the current state of an export job."""

    kind: JobStatusKind
    reason: str | None = None

    def __post_init__(self) -> None:
        """Enforce the invariant that reason is set if and only if the kind is failed."""
        if self.kind is JobStatusKind.FAILED and self.reason is None:
            raise InvalidJobStatusError(message="Failed job status requires a reason")
        if self.kind is not JobStatusKind.FAILED and self.reason is not None:
            raise InvalidJobStatusError(message="Reason is only allowed on failed status")

    @classmethod
    def pending(cls) -> Self:
        """Construct a pending status (the state a freshly-created job starts in)."""
        return cls(kind=JobStatusKind.PENDING)

    @classmethod
    def success(cls) -> Self:
        """Construct a successful status."""
        return cls(kind=JobStatusKind.SUCCESS)

    @classmethod
    def failed(cls, reason: str) -> Self:
        """Construct a failed status carrying the given reason."""
        return cls(kind=JobStatusKind.FAILED, reason=reason)
