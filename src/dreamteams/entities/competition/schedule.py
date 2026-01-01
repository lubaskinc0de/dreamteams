from dataclasses import dataclass
from datetime import UTC, datetime

from dreamteams.entities.errors.competition import InvalidCompetitionDataError


def normalize_datetime(dt: datetime) -> datetime:
    """Normalize datetime by removing seconds and microseconds."""
    return dt.replace(second=0, microsecond=0)


@dataclass(slots=True)
class CompetitionSchedule:
    """Competition schedule with registration and optional team formation periods."""

    registration_start: datetime
    registration_end: datetime
    team_formation_start: datetime | None = None
    team_formation_end: datetime | None = None

    def __post_init__(self) -> None:
        """Validate schedule dates and normalize datetime values."""
        if (self.team_formation_start is None) != (self.team_formation_end is None):
            raise InvalidCompetitionDataError(
                message="Both team formation start and end must be specified together or not at all",
            )

        now = normalize_datetime(datetime.now(tz=UTC))

        self._normalize_all_dates()
        self._validate_dates_not_in_past(now)
        self._validate_date_ranges()

    def _normalize_all_dates(self) -> None:
        """Normalize all datetime values."""
        self.registration_start = normalize_datetime(self.registration_start)
        self.registration_end = normalize_datetime(self.registration_end)

        if self.team_formation_start is not None:
            self.team_formation_start = normalize_datetime(self.team_formation_start)
        if self.team_formation_end is not None:
            self.team_formation_end = normalize_datetime(self.team_formation_end)

    def _validate_dates_not_in_past(self, now: datetime) -> None:
        """Validate that all dates are not in the past."""
        if self.registration_start < now:
            raise InvalidCompetitionDataError(message="Registration start date must not be in the past")
        if self.registration_end < now:
            raise InvalidCompetitionDataError(message="Registration end date must not be in the past")

        if self.team_formation_start is not None and self.team_formation_end is not None:
            if self.team_formation_start < now:
                raise InvalidCompetitionDataError(message="Team formation start date must not be in the past")
            if self.team_formation_end < now:
                raise InvalidCompetitionDataError(message="Team formation end date must not be in the past")

    def _validate_date_ranges(self) -> None:
        """Validate date ranges are correct."""
        if self.registration_start >= self.registration_end:
            raise InvalidCompetitionDataError(message="Registration start date must be before end date")

        if self.team_formation_start is not None and self.team_formation_end is not None:
            if self.team_formation_start < self.registration_end:
                raise InvalidCompetitionDataError(
                    message="Team formation start must be after or equal to registration end",
                )

            if self.team_formation_end <= self.team_formation_start:
                raise InvalidCompetitionDataError(message="Team formation end must be after start")
