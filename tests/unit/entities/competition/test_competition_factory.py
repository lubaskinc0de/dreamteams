from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker

from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import Competition, competition_factory
from dreamteams.entities.competition.milestone import Milestone, MilestoneData
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionFormat, CompetitionVenue
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams.entities.user import User


@pytest.mark.parametrize(
    (
        "domains",
        "participant_type",
        "venue_format",
        "location",
        "participant_max",
        "participant_min",
        "team_max",
        "team_min",
        "reg_start",
        "reg_end",
    ),
    [
        # Standard online competition: 10-day registration
        (
            [Domain.AI, Domain.BACKEND],
            ParticipantType.STUDENT,
            CompetitionFormat.ONLINE,
            None,
            100,  # max participants
            10,  # min participants
            5,  # max team size
            1,  # min team size (solo allowed)
            timedelta(days=1),
            timedelta(days=10),
        ),
        # Large hybrid competition: 1-month registration
        (
            [Domain.AI, Domain.BACKEND, Domain.MOBILE, Domain.DEVOPS],
            ParticipantType.ANY,
            CompetitionFormat.HYBRID,
            "Moscow, Russia",
            500,  # max participants
            50,  # min participants
            10,  # max team size
            3,  # min team size (no solo participants)
            timedelta(days=7),
            timedelta(days=37),
        ),
        # Small offline competition: 8-day registration
        (
            [Domain.FRONTEND],
            ParticipantType.SCHOOLCHILD,
            CompetitionFormat.OFFLINE,
            "Saint Petersburg, Russia",
            30,  # max participants
            5,  # min participants
            1,  # max team size (solo only)
            1,  # min team size (solo only)
            timedelta(days=2),
            timedelta(days=10),
        ),
    ],
)
def test_create_competition_with_valid_data(
    faker: Faker,
    organizer_user: User,
    domains: list[Domain],
    participant_type: ParticipantType,
    venue_format: CompetitionFormat,
    location: str | None,
    participant_max: int,
    participant_min: int,
    team_max: int,
    team_min: int,
    reg_start: timedelta,
    reg_end: timedelta,
) -> None:
    """Test creating competition with different configurations."""
    now = datetime.now(tz=UTC)
    title = faker.sentence(nb_words=4)
    description = faker.text(max_nb_chars=200)
    schedule = CompetitionSchedule(
        registration_start=now + reg_start,
        registration_end=now + reg_end,
        team_formation_end=None,
        team_formation_start=None,
    )
    participant_limits = ParticipantLimits(max=participant_max, min=participant_min)
    venue = CompetitionVenue(format=venue_format, location=location)
    team_size = TeamSizeRange(max=team_max, min=team_min)

    competition = competition_factory(
        user=organizer_user,
        title=title,
        description=description,
        schedule=ScheduleData(
            schedule.registration_start,
            schedule.registration_end,
            schedule.team_formation_start,
            schedule.team_formation_end,
        ),
        participant_limits=participant_limits,
        domains=domains,
        participant_type=participant_type,
        venue=venue,
        team_size=team_size,
    )

    assert organizer_user.organizer is not None
    assert competition.created_at == competition.updated_at
    assert competition == Competition(
        id=competition.id,
        organizer_id=organizer_user.organizer.id,
        title=title,
        description=description,
        schedule=schedule,
        participant_limits=participant_limits,
        domains=domains,
        participant_type=participant_type,
        venue=venue,
        team_size=team_size,
        banner=None,
        is_archived=True,
        milestones=[],
        created_at=competition.created_at,
        updated_at=competition.updated_at,
    )


@pytest.mark.parametrize(
    ("description", "test_domains", "expected_error"),
    [
        # Description cannot be empty string
        ("", [Domain.AI], "Description must not be empty"),
        # Description cannot be whitespace only
        ("   ", [Domain.AI], "Description must not be empty"),
        # Domains list cannot be empty
        ("Valid description", [], "Domains list must not be empty"),
    ],
)
def test_create_competition_with_invalid_data_raises_error(
    faker: Faker,
    organizer_user: User,
    valid_schedule_data: ScheduleData,
    participant_limits: ParticipantLimits,
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
    description: str,
    test_domains: list[Domain],
    expected_error: str,
) -> None:
    """Test that invalid data raises appropriate errors."""
    with pytest.raises(InvalidCompetitionDataError, match=expected_error):
        competition_factory(
            user=organizer_user,
            title=faker.sentence(nb_words=3),
            description=description,
            schedule=valid_schedule_data,
            participant_limits=participant_limits,
            domains=test_domains,
            participant_type=ParticipantType.STUDENT,
            venue=venue,
            team_size=team_size,
        )


def test_competition_created_at_and_updated_at_are_set(
    faker: Faker,
    organizer_user: User,
    valid_schedule_data: ScheduleData,
    participant_limits: ParticipantLimits,
    domains: list[Domain],
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
) -> None:
    """Test that created_at and updated_at are set to current time."""
    competition = competition_factory(
        user=organizer_user,
        title=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=150),
        schedule=valid_schedule_data,
        participant_limits=participant_limits,
        domains=domains,
        participant_type=ParticipantType.STUDENT,
        venue=venue,
        team_size=team_size,
    )

    time_diff = (datetime.now(tz=UTC) - competition.created_at).total_seconds()
    assert time_diff < 1
    assert competition.created_at.tzinfo == UTC
    assert competition.updated_at.tzinfo == UTC


def test_create_competition_with_valid_milestones(
    faker: Faker,
    organizer_user: User,
    valid_schedule_data: ScheduleData,
    participant_limits: ParticipantLimits,
    domains: list[Domain],
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
    milestones: list[Milestone],
) -> None:
    """Test creating competition with valid milestones."""
    competition = competition_factory(
        user=organizer_user,
        title=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=150),
        schedule=valid_schedule_data,
        participant_limits=participant_limits,
        domains=domains,
        participant_type=ParticipantType.STUDENT,
        venue=venue,
        team_size=team_size,
        milestones=[MilestoneData(milestone.title, milestone.timestamp) for milestone in milestones],
    )

    assert competition.milestones == milestones


def test_create_competition_with_duplicate_milestone_timestamps_raises_error(
    faker: Faker,
    organizer_user: User,
    valid_schedule_data: ScheduleData,
    participant_limits: ParticipantLimits,
    domains: list[Domain],
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
) -> None:
    """Test that duplicate milestone timestamps raise error."""
    now = datetime.now(tz=UTC)
    duplicate_timestamp = now + timedelta(days=15)
    duplicate_milestones = [
        MilestoneData(timestamp=duplicate_timestamp, title="Stage 1"),
        MilestoneData(timestamp=duplicate_timestamp, title="Stage 2"),
    ]

    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamps must be unique"):
        competition_factory(
            user=organizer_user,
            title=faker.sentence(nb_words=3),
            description=faker.text(max_nb_chars=150),
            schedule=valid_schedule_data,
            participant_limits=participant_limits,
            domains=domains,
            participant_type=ParticipantType.STUDENT,
            venue=venue,
            team_size=team_size,
            milestones=duplicate_milestones,
        )
