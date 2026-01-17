from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker

from dreamteams.entities.competition.milestone import MilestoneData, milestone_factory
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


def test_create_milestone_with_valid_data() -> None:
    """Test creating Milestone with valid timestamp and title."""
    timestamp = datetime.now(tz=UTC) + timedelta(days=1)
    title = "Stage 1"

    milestone = milestone_factory(MilestoneData(timestamp=timestamp, title=title))

    assert milestone.timestamp == timestamp.replace(second=0, microsecond=0)
    assert milestone.title == title


@pytest.mark.parametrize(
    ("title", "expected_error"),
    [
        ("", "Milestone title must not be empty"),
        ("   ", "Milestone title must not be empty"),
        ("\t\n", "Milestone title must not be empty"),
    ],
)
def test_create_milestone_with_invalid_title_raises_error(title: str, expected_error: str) -> None:
    """Test that empty or whitespace-only titles raise appropriate errors."""
    timestamp = datetime.now(tz=UTC) + timedelta(days=1)

    with pytest.raises(InvalidCompetitionDataError, match=expected_error):
        milestone_factory(MilestoneData(timestamp=timestamp, title=title))


@pytest.mark.parametrize(
    ("delta"),
    [
        timedelta(days=-1),
    ],
)
def test_cannot_create_milestone_with_timestamp_in_past(delta: timedelta, faker: Faker) -> None:
    """Test that empty or whitespace-only titles raise appropriate errors."""
    timestamp = datetime.now(tz=UTC) + delta

    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamp cannot be in past"):
        milestone_factory(MilestoneData(timestamp=timestamp, title=faker.sentence(nb_words=4)))
