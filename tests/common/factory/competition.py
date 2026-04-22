from datetime import UTC, datetime, timedelta

from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.application.common.dto.milestone import MilestoneForm
from dreamteams.application.manage_competitions import UpdateCompetitionForm
from dreamteams.application.publish_competition import CompetitionForm
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionFormat, CompetitionVenue


def _competition_schedule_provider() -> ScheduleData:
    """Provider for CompetitionSchedule with random but valid dates, including team formation."""
    now = datetime.now(tz=UTC)
    random_ = CompetitionFormFactory.__random__
    reg_start_offset = random_.randint(1, 10)
    reg_duration = random_.randint(5, 30)

    registration_start = now + timedelta(days=reg_start_offset)
    registration_end = registration_start + timedelta(days=reg_duration)

    team_formation_duration = random_.randint(1, 7)
    team_formation_start = registration_end
    team_formation_end = team_formation_start + timedelta(days=team_formation_duration)

    return ScheduleData(
        registration_start=registration_start,
        registration_end=registration_end,
        team_formation_start=team_formation_start,
        team_formation_end=team_formation_end,
    )


def _participant_limits_provider() -> ParticipantLimits:
    """Provider for ParticipantLimits with a random but valid max value."""
    random_ = CompetitionFormFactory.__random__
    return ParticipantLimits(max=random_.randint(5, 150))


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


def _milestones_provider() -> list[MilestoneForm]:
    """Provider for milestones list with random but valid dates."""
    random_ = CompetitionFormFactory.__random__
    faker = CompetitionFormFactory.__faker__
    now = datetime.now(tz=UTC)

    count = random_.randint(0, 10)
    if count == 0:
        return []

    milestones = []
    timestamps = set()
    for i in range(count):
        days_offset = random_.randint(1, 30) + i * 5
        description = faker.paragraph(nb_sentences=2)[:300] if random_.choice([True, False]) else None
        milestone_form = MilestoneForm(
            timestamp=now + timedelta(days=days_offset),
            title=faker.sentence(nb_words=3),
            description=description,
        )

        if milestone_form.timestamp in timestamps:
            continue

        timestamps.add(milestone_form.timestamp)
        milestones.append(milestone_form)

    return milestones


class CompetitionFormFactory(ModelFactory[CompetitionForm]):
    """Factory of CompetitionForm models."""

    __model__ = CompetitionForm

    schedule = _competition_schedule_provider
    participant_limits = _participant_limits_provider
    venue = _competition_venue_provider
    team_size = _team_size_provider
    domains = _domains_provider
    participant_type = _participant_type_provider
    milestones = _milestones_provider


class UpdateCompetitionFormFactory(ModelFactory[UpdateCompetitionForm]):
    """Factory of UpdateCompetitionForm models."""

    __model__ = UpdateCompetitionForm

    schedule = _competition_schedule_provider
    participant_limits = _participant_limits_provider
    venue = _competition_venue_provider
    team_size = _team_size_provider
    domains = _domains_provider
    participant_type = _participant_type_provider
    milestones = _milestones_provider
