from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker

from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition import (
    CompetitionFormat,
    CompetitionSchedule,
    CompetitionVenue,
    ParticipantLimits,
    TeamSizeRange,
    competition_factory,
)
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@pytest.mark.parametrize(
    ("domains", "participant_type", "venue_format", "location"),
    [
        ([Domain.AI, Domain.BACKEND], ParticipantType.STUDENT, CompetitionFormat.ONLINE, None),
        (
            [Domain.AI, Domain.BACKEND, Domain.MOBILE, Domain.DEVOPS],
            ParticipantType.ANY,
            CompetitionFormat.HYBRID,
            "Moscow, Russia",
        ),
        ([Domain.FRONTEND], ParticipantType.SCHOOLCHILD, CompetitionFormat.OFFLINE, "Saint Petersburg, Russia"),
    ],
)
def test_create_competition_with_valid_data(
    faker: Faker,
    domains: list[Domain],
    participant_type: ParticipantType,
    venue_format: CompetitionFormat,
    location: str | None,
) -> None:
    """Test creating competition with valid data."""
    now = datetime.now(tz=UTC)
    organizer_id = faker.uuid4(cast_to=None)
    title = faker.sentence(nb_words=4)
    description = faker.text(max_nb_chars=200)
    schedule = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
        competition_start=now + timedelta(days=11),
        competition_end=now + timedelta(days=15),
    )
    participant_limits = ParticipantLimits(max=100, min=10)
    venue = CompetitionVenue(format=venue_format, location=location)
    team_size = TeamSizeRange(max=5, min=1)

    competition = competition_factory(
        organizer_id=organizer_id,
        title=title,
        description=description,
        schedule=schedule,
        participant_limits=participant_limits,
        domains=domains,
        participant_type=participant_type,
        venue=venue,
        team_size=team_size,
    )

    assert competition.organizer_id == organizer_id
    assert competition.title == title
    assert competition.description == description
    assert competition.schedule == schedule
    assert competition.participant_limits == participant_limits
    assert competition.domains == domains
    assert competition.participant_type == participant_type
    assert competition.venue == venue
    assert competition.team_size == team_size
    assert competition.banner is None
    assert competition.is_archived is True
    assert competition.created_at == competition.updated_at


@pytest.mark.parametrize(
    ("description", "domains", "expected_error"),
    [
        ("", [Domain.AI], "Description must not be empty"),
        ("   ", [Domain.AI], "Description must not be empty"),
        ("Valid description", [], "Domains list must not be empty"),
    ],
)
def test_create_competition_with_invalid_data_raises_error(
    faker: Faker,
    description: str,
    domains: list[Domain],
    expected_error: str,
) -> None:
    """Test that invalid data raises appropriate errors."""
    now = datetime.now(tz=UTC)
    organizer_id = faker.uuid4(cast_to=None)
    schedule = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
        competition_start=now + timedelta(days=11),
        competition_end=now + timedelta(days=15),
    )

    with pytest.raises(InvalidCompetitionDataError, match=expected_error):
        competition_factory(
            organizer_id=organizer_id,
            title=faker.sentence(nb_words=3),
            description=description,
            schedule=schedule,
            participant_limits=ParticipantLimits(max=100, min=10),
            domains=domains,
            participant_type=ParticipantType.STUDENT,
            venue=CompetitionVenue(format=CompetitionFormat.ONLINE, location=None),
            team_size=TeamSizeRange(max=5, min=1),
        )


def test_competition_created_at_and_updated_at_are_set(faker: Faker) -> None:
    """Test that created_at and updated_at are set to current time."""
    now = datetime.now(tz=UTC)
    organizer_id = faker.uuid4(cast_to=None)
    schedule = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
        competition_start=now + timedelta(days=11),
        competition_end=now + timedelta(days=15),
    )

    competition = competition_factory(
        organizer_id=organizer_id,
        title=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=150),
        schedule=schedule,
        participant_limits=ParticipantLimits(max=100, min=10),
        domains=[Domain.AI],
        participant_type=ParticipantType.STUDENT,
        venue=CompetitionVenue(format=CompetitionFormat.ONLINE, location=None),
        team_size=TeamSizeRange(max=5, min=1),
    )

    time_diff = (datetime.now(tz=UTC) - competition.created_at).total_seconds()
    assert time_diff < 1
    assert competition.created_at.tzinfo == UTC
    assert competition.updated_at.tzinfo == UTC
