from dataclasses import dataclass
from datetime import datetime

from dreamteams.entities.common.datetime_utils import normalize_datetime
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams_common.clock import Clock


@dataclass(slots=True)
class ScheduleData:
    """Schedule creation data."""

    registration_start: datetime
    registration_end: datetime
    team_formation_start: datetime | None = None
    team_formation_end: datetime | None = None


@dataclass(slots=True)
class CompetitionSchedule:
    """Competition schedule with registration and optional team formation periods."""

    registration_start: datetime
    registration_end: datetime
    team_formation_start: datetime | None
    team_formation_end: datetime | None

    def __post_init__(self) -> None:
        """Validate schedule dates and normalize datetime values."""
        self._normalize_all_dates()
        self._validate_date_ranges()

    def _normalize_all_dates(self) -> None:
        """Normalize all datetime values."""
        self.registration_start = normalize_datetime(self.registration_start)
        self.registration_end = normalize_datetime(self.registration_end)

        if self.team_formation_start is not None:
            self.team_formation_start = normalize_datetime(self.team_formation_start)
        if self.team_formation_end is not None:
            self.team_formation_end = normalize_datetime(self.team_formation_end)

    def _validate_date_ranges(self) -> None:
        """Validate date ranges are correct."""
        if (self.team_formation_start is None) != (self.team_formation_end is None):
            raise InvalidCompetitionDataError(
                message="Both team formation start and end must be specified together or not at all",
            )

        if self.registration_start >= self.registration_end:
            raise InvalidCompetitionDataError(message="Registration start date must be before end date")

        if self.team_formation_start is not None and self.team_formation_end is not None:
            if self.team_formation_start < self.registration_end:
                raise InvalidCompetitionDataError(
                    message="Team formation start must be after or equal to registration end",
                )

            if self.team_formation_end <= self.team_formation_start:
                raise InvalidCompetitionDataError(message="Team formation end must be after start")

    def update(self, data: ScheduleData, clock: Clock) -> "CompetitionSchedule":
        """Update schedule."""
        now = normalize_datetime(clock.now())

        tf_start = self.team_formation_start
        tf_end = self.team_formation_end

        if self.team_formation_start is None or self.team_formation_start > now:
            tf_start = data.team_formation_start
        if self.team_formation_end is None or self.team_formation_end > now:
            tf_end = data.team_formation_end

        return CompetitionSchedule(
            self.registration_start if self.registration_start < now else data.registration_start,
            self.registration_end if self.registration_end < now else data.registration_end,
            tf_start,
            tf_end,
        )


def _validate_dates_not_in_past(
    registration_start: datetime,
    registration_end: datetime,
    team_formation_start: datetime | None,
    team_formation_end: datetime | None,
    now: datetime,
) -> None:
    """Validate that schedule dates are not in past."""
    if registration_start < now:
        raise InvalidCompetitionDataError(message="Registration start date must not be in the past")
    if registration_end < now:
        raise InvalidCompetitionDataError(message="Registration end date must not be in the past")

    if team_formation_start is not None and team_formation_end is not None:
        if team_formation_start < now:
            raise InvalidCompetitionDataError(message="Team formation start date must not be in the past")
        if team_formation_end < now:
            raise InvalidCompetitionDataError(message="Team formation end date must not be in the past")


def schedule_factory(
    data: ScheduleData,
    clock: Clock,
) -> CompetitionSchedule:
    """Create new schedule."""
    now = normalize_datetime(clock.now())
    _validate_dates_not_in_past(
        data.registration_start,
        data.registration_end,
        data.team_formation_start,
        data.team_formation_end,
        now,
    )
    return CompetitionSchedule(
        data.registration_start,
        data.registration_end,
        data.team_formation_start,
        data.team_formation_end,
    )
