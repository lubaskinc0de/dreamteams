from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker

from dreamteams.adapters.clock import SystemClock
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import Competition, competition_factory
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionFormat, CompetitionVenue
from dreamteams.entities.organizer import Organizer
from dreamteams.entities.user import User


def utc(dt_string: str) -> datetime:
    """Create UTC datetime from string in format 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)


@pytest.fixture
def organizer_user(faker: Faker) -> User:
    """User with organizer role attached."""
    user_id = faker.uuid4(cast_to=None)
    organizer_id = faker.uuid4(cast_to=None)

    organizer = Organizer(
        id=organizer_id,
        user_id=user_id,
        organizer_name=faker.company(),
        phone_number=faker.phone_number(),
        contact_email=faker.email(),
        logo=None,
    )

    return User(id=user_id, organizer=organizer)


@pytest.fixture
def different_user(faker: Faker) -> User:
    """Different user with different organizer role attached."""
    user_id = faker.uuid4(cast_to=None)
    organizer_id = faker.uuid4(cast_to=None)

    organizer = Organizer(
        id=organizer_id,
        user_id=user_id,
        organizer_name=faker.company(),
        phone_number=faker.phone_number(),
        contact_email=faker.email(),
        logo=None,
    )

    return User(id=user_id, organizer=organizer)


@pytest.fixture
def user_without_organizer(faker: Faker) -> User:
    """User without organizer role."""
    return User(id=faker.uuid4(cast_to=None), organizer=None)


@pytest.fixture(scope="module")
def clock() -> Clock:
    """Real system clock for tests."""
    return SystemClock()


@pytest.fixture
def valid_schedule_data(clock: Clock) -> ScheduleData:
    """Valid schedule data with team formation period."""
    now = clock.now()
    return ScheduleData(
        registration_start=now + timedelta(days=5),
        registration_end=now + timedelta(days=15),
        team_formation_start=now + timedelta(days=20),
        team_formation_end=now + timedelta(days=30),
    )


@pytest.fixture
def schedule(valid_schedule_data: ScheduleData) -> CompetitionSchedule:
    """Competition schedule for tests."""
    return CompetitionSchedule(
        registration_start=valid_schedule_data.registration_start,
        registration_end=valid_schedule_data.registration_end,
        team_formation_start=valid_schedule_data.team_formation_start,
        team_formation_end=valid_schedule_data.team_formation_end,
    )


@pytest.fixture
def participant_limits() -> ParticipantLimits:
    """Participant limits for tests."""
    return ParticipantLimits(max=100, min=10)


@pytest.fixture
def domains() -> list[Domain]:
    """Domains for tests."""
    return [Domain.AI]


@pytest.fixture
def venue() -> CompetitionVenue:
    """Venue for tests."""
    return CompetitionVenue(format=CompetitionFormat.ONLINE, location=None)


@pytest.fixture
def team_size() -> TeamSizeRange:
    """Team size range for tests."""
    return TeamSizeRange(max=5, min=1)


@pytest.fixture
def milestones(clock: Clock) -> list[Milestone]:
    """Milestones for tests."""
    now = clock.now()
    return [
        Milestone(timestamp=now + timedelta(days=35), title="Stage 1"),
        Milestone(timestamp=now + timedelta(days=45), title="Stage 2"),
    ]


@pytest.fixture
def competition(
    faker: Faker,
    organizer_user: User,
    valid_schedule_data: ScheduleData,
    participant_limits: ParticipantLimits,
    domains: list[Domain],
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
    clock: Clock,
) -> Competition:
    """Competition created by organizer_user."""
    return competition_factory(
        user=organizer_user,
        title=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=150),
        schedule=valid_schedule_data,
        participant_limits=participant_limits,
        domains=domains,
        participant_type=ParticipantType.STUDENT,
        venue=venue,
        team_size=team_size,
        clock=clock,
    )


@pytest.fixture(scope="module")
def faker() -> Faker:
    """Provide faker instance."""
    return Faker()
