from datetime import datetime

import pytest
from faker import Faker
from freezegun import freeze_time

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.competition.milestone import MilestoneData, milestone_factory
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from tests.unit.entities.competition.conftest import utc


@freeze_time("2025-01-15 12:00:00")
def test_create_milestone_with_valid_data(clock: Clock) -> None:
    """Test creating Milestone with valid timestamp and title."""
    timestamp = utc("2026-02-20 14:30:00")
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
    timestamp = utc("2026-02-20 14:30:00")

    with pytest.raises(InvalidCompetitionDataError, match="Milestone title must not be empty"):
        milestone_factory(MilestoneData(timestamp=timestamp, title=title), clock)


@pytest.mark.parametrize(
    "timestamp",
    [
        utc("2024-12-01 10:00:00"),
        utc("2025-01-15 12:00:00"),
    ],
)
@freeze_time("2025-01-15 12:00:00")
def test_timestamp_must_be_in_future(clock: Clock, faker: Faker, timestamp: datetime) -> None:
    """Test that milestone with timestamp in past raises error."""
    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamp cannot be in past"):
        milestone_factory(MilestoneData(timestamp=timestamp, title=faker.sentence(nb_words=4)), clock)
