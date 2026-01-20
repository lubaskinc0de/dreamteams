from datetime import UTC, datetime

import pytest
from faker import Faker
from freezegun import freeze_time

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.milestone import MilestoneData, milestone_factory
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@freeze_time("2025-01-15 12:00:00")
def test_create_milestone_with_valid_data(clock: Clock) -> None:
    """Test creating Milestone with valid timestamp and title."""
    timestamp = datetime(year=2026, month=2, day=20, hour=14, minute=30, tzinfo=UTC)
    title = "Stage 1"

    milestone = milestone_factory(MilestoneData(timestamp=timestamp, title=title), clock)

    assert milestone.timestamp == timestamp.replace(second=0, microsecond=0)
    assert milestone.title == title


@pytest.mark.parametrize(
    ("title"),
    [
        (""),
        ("   "),
        ("\t\n"),
    ],
)
@freeze_time("2025-01-15 12:00:00")
def test_title_is_not_empty(clock: Clock, title: str) -> None:
    """Test that empty or whitespace-only titles raise error."""
    timestamp = datetime(year=2026, month=2, day=20, hour=14, minute=30, tzinfo=UTC)

    with pytest.raises(InvalidCompetitionDataError, match="Milestone title must not be empty"):
        milestone_factory(MilestoneData(timestamp=timestamp, title=title), clock)


@freeze_time("2025-01-15 12:00:00")
def test_timestamp_must_be_in_future(clock: Clock, faker: Faker) -> None:
    """Test that milestone with timestamp in past raises error."""
    timestamp = datetime(year=2024, month=12, day=1, hour=10, minute=0, tzinfo=UTC)

    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamp cannot be in past"):
        milestone_factory(MilestoneData(timestamp=timestamp, title=faker.sentence(nb_words=4)), clock)
