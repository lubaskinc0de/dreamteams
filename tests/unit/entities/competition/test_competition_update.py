from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker

from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import competition_factory
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionFormat, CompetitionVenue
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams.entities.organizer import Organizer
from dreamteams.entities.user import User


def test_update_competition_with_valid_milestones(faker: Faker) -> None:
    """Test updating competition with valid milestones."""
    now = datetime.now(tz=UTC)
    organizer_id = faker.uuid4(cast_to=None)
    user_id = faker.uuid4(cast_to=None)
    schedule = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
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

    organizer = Organizer(
        id=organizer_id,
        user_id=user_id,
        organizer_name=faker.company(),
        phone_number=faker.phone_number(),
        contact_email=faker.email(),
        logo=None,
    )
    user = User(id=user_id, organizer=organizer)
    new_milestones = [
        Milestone(timestamp=now + timedelta(days=15), title="Stage 1"),
        Milestone(timestamp=now + timedelta(days=20), title="Stage 2"),
    ]

    competition.update(
        user=user,
        title="Updated Title",
        description="Updated description",
        schedule=schedule,
        participant_limits=ParticipantLimits(max=100, min=10),
        domains=[Domain.AI],
        participant_type=ParticipantType.STUDENT,
        venue=CompetitionVenue(format=CompetitionFormat.ONLINE, location=None),
        team_size=TeamSizeRange(max=5, min=1),
        milestones=new_milestones,
        is_archived=False,
    )

    assert competition.milestones == new_milestones


def test_update_competition_with_duplicate_milestone_timestamps_raises_error(faker: Faker) -> None:
    """Test that updating competition with duplicate milestone timestamps raises error."""
    now = datetime.now(tz=UTC)
    organizer_id = faker.uuid4(cast_to=None)
    user_id = faker.uuid4(cast_to=None)
    schedule = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
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

    organizer = Organizer(
        id=organizer_id,
        user_id=user_id,
        organizer_name=faker.company(),
        phone_number=faker.phone_number(),
        contact_email=faker.email(),
        logo=None,
    )
    user = User(id=user_id, organizer=organizer)
    duplicate_timestamp = now + timedelta(days=15)
    duplicate_milestones = [
        Milestone(timestamp=duplicate_timestamp, title="Stage 1"),
        Milestone(timestamp=duplicate_timestamp, title="Stage 2"),
    ]

    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamps must be unique"):
        competition.update(
            user=user,
            title="Updated Title",
            description="Updated description",
            schedule=schedule,
            participant_limits=ParticipantLimits(max=100, min=10),
            domains=[Domain.AI],
            participant_type=ParticipantType.STUDENT,
            venue=CompetitionVenue(format=CompetitionFormat.ONLINE, location=None),
            team_size=TeamSizeRange(max=5, min=1),
            milestones=duplicate_milestones,
            is_archived=False,
        )


@pytest.mark.parametrize(
    ("description", "domains", "expected_error"),
    [
        ("", [Domain.AI], "Description must not be empty"),
        ("   ", [Domain.AI], "Description must not be empty"),
        ("Valid description", [], "Domains list must not be empty"),
    ],
)
def test_update_competition_with_invalid_data_raises_error(
    faker: Faker,
    description: str,
    domains: list[Domain],
    expected_error: str,
) -> None:
    """Test that updating with invalid data raises appropriate errors."""
    now = datetime.now(tz=UTC)
    organizer_id = faker.uuid4(cast_to=None)
    user_id = faker.uuid4(cast_to=None)
    schedule = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
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

    organizer = Organizer(
        id=organizer_id,
        user_id=user_id,
        organizer_name=faker.company(),
        phone_number=faker.phone_number(),
        contact_email=faker.email(),
        logo=None,
    )
    user = User(id=user_id, organizer=organizer)

    with pytest.raises(InvalidCompetitionDataError, match=expected_error):
        competition.update(
            user=user,
            title="Updated Title",
            description=description,
            schedule=schedule,
            participant_limits=ParticipantLimits(max=100, min=10),
            domains=domains,
            participant_type=ParticipantType.STUDENT,
            venue=CompetitionVenue(format=CompetitionFormat.ONLINE, location=None),
            team_size=TeamSizeRange(max=5, min=1),
            milestones=[],
            is_archived=False,
        )


def test_update_competition_by_non_organizer_raises_error(faker: Faker) -> None:
    """Test that updating competition by non-organizer raises error."""
    now = datetime.now(tz=UTC)
    organizer_id = faker.uuid4(cast_to=None)
    schedule = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
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

    # User without organizer
    user_without_organizer = User(id=faker.uuid4(cast_to=None), organizer=None)

    with pytest.raises(AccessDeniedError):
        competition.update(
            user=user_without_organizer,
            title="Updated Title",
            description="Updated description",
            schedule=schedule,
            participant_limits=ParticipantLimits(max=100, min=10),
            domains=[Domain.AI],
            participant_type=ParticipantType.STUDENT,
            venue=CompetitionVenue(format=CompetitionFormat.ONLINE, location=None),
            team_size=TeamSizeRange(max=5, min=1),
            milestones=[],
            is_archived=False,
        )


def test_update_competition_by_different_organizer_raises_error(faker: Faker) -> None:
    """Test that updating competition by different organizer raises error."""
    now = datetime.now(tz=UTC)
    organizer_id = faker.uuid4(cast_to=None)
    schedule = CompetitionSchedule(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
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

    # User with different organizer
    different_organizer_id = faker.uuid4(cast_to=None)
    different_user_id = faker.uuid4(cast_to=None)
    different_organizer = Organizer(
        id=different_organizer_id,
        user_id=different_user_id,
        organizer_name=faker.company(),
        phone_number=faker.phone_number(),
        contact_email=faker.email(),
        logo=None,
    )
    user_different_organizer = User(id=different_user_id, organizer=different_organizer)

    with pytest.raises(AccessDeniedError):
        competition.update(
            user=user_different_organizer,
            title="Updated Title",
            description="Updated description",
            schedule=schedule,
            participant_limits=ParticipantLimits(max=100, min=10),
            domains=[Domain.AI],
            participant_type=ParticipantType.STUDENT,
            venue=CompetitionVenue(format=CompetitionFormat.ONLINE, location=None),
            team_size=TeamSizeRange(max=5, min=1),
            milestones=[],
            is_archived=False,
        )
