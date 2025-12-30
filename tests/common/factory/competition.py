from datetime import UTC, datetime, timedelta

from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.application.create_competition.interactor import CompetitionForm
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition import (
    CompetitionFormat,
    CompetitionSchedule,
    CompetitionVenue,
    ParticipantLimits,
    TeamSizeRange,
)


def _competition_schedule_provider() -> CompetitionSchedule:
    """Provider for CompetitionSchedule with random but valid dates."""
    now = datetime.now(tz=UTC)
    random_ = CompetitionFormFactory.__random__
    reg_start_offset = random_.randint(1, 10)
    reg_duration = random_.randint(5, 30)
    comp_start_offset = random_.randint(1, 5)
    comp_duration = random_.randint(1, 7)

    registration_start = now + timedelta(days=reg_start_offset)
    registration_end = registration_start + timedelta(days=reg_duration)
    competition_start = registration_end + timedelta(days=comp_start_offset)
    competition_end = competition_start + timedelta(days=comp_duration)

    team_formation_start = None
    team_formation_end = None
    if random_.choice([True, False]):
        team_formation_duration = random_.randint(1, comp_start_offset - 1) if comp_start_offset > 1 else 1
        team_formation_start = registration_end
        team_formation_end = team_formation_start + timedelta(days=team_formation_duration)
        team_formation_end = min(team_formation_end, competition_end)

    return CompetitionSchedule(
        competition_start=competition_start,
        competition_end=competition_end,
        registration_start=registration_start,
        registration_end=registration_end,
        team_formation_start=team_formation_start,
        team_formation_end=team_formation_end,
    )


def _participant_limits_provider() -> ParticipantLimits:
    """Provider for ParticipantLimits with random but valid values."""
    random_ = CompetitionFormFactory.__random__
    min_participants = random_.randint(5, 50)
    max_participants = random_.randint(min_participants, min_participants + 100)
    return ParticipantLimits(max=max_participants, min=min_participants)


def _competition_venue_provider() -> CompetitionVenue:
    """Provider for CompetitionVenue with random format and location when needed."""
    faker = CompetitionFormFactory.__faker__
    random_ = CompetitionFormFactory.__random__

    format_choice = random_.choice(list(CompetitionFormat))
    location = faker.address() if format_choice in (CompetitionFormat.OFFLINE, CompetitionFormat.HYBRID) else None
    return CompetitionVenue(format=format_choice, location=location)


def _team_size_provider() -> TeamSizeRange:
    """Provider for TeamSizeRange with random but valid values."""
    random_ = CompetitionFormFactory.__random__
    min_size = random_.randint(1, 5)
    max_size = random_.randint(min_size, 10)
    return TeamSizeRange(max=max_size, min=min_size)


def _domains_provider() -> list[Domain]:
    """Provider for domains list with random selection."""
    random_ = CompetitionFormFactory.__random__
    all_domains = list(Domain)
    count = random_.randint(1, len(all_domains))
    return random_.sample(all_domains, count)


def _participant_type_provider() -> ParticipantType:
    """Provider for ParticipantType with random selection."""
    random_ = CompetitionFormFactory.__random__
    return random_.choice(list(ParticipantType))


class CompetitionFormFactory(ModelFactory[CompetitionForm]):
    """Factory of CompetitionForm models."""

    __model__ = CompetitionForm

    schedule = _competition_schedule_provider
    participant_limits = _participant_limits_provider
    venue = _competition_venue_provider
    team_size = _team_size_provider
    domains = _domains_provider
    participant_type = _participant_type_provider
