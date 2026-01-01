from datetime import UTC, datetime

import pytest

from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


def test_create_milestone_with_valid_data() -> None:
    """Test creating Milestone with valid timestamp and title."""
    timestamp = datetime(2024, 10, 24, tzinfo=UTC)
    title = "Stage 1"

    milestone = Milestone(timestamp=timestamp, title=title)

    assert milestone.timestamp == timestamp
    assert milestone.title == title


def test_milestone_timestamp_normalization() -> None:
    """Test that Milestone normalizes timestamp by removing seconds and microseconds."""
    timestamp_with_seconds = datetime(2024, 10, 24, 14, 30, 45, 123456, tzinfo=UTC)
    expected_normalized = datetime(2024, 10, 24, 14, 30, 0, 0, tzinfo=UTC)

    milestone = Milestone(timestamp=timestamp_with_seconds, title="Stage 1")

    assert milestone.timestamp == expected_normalized
    assert milestone.timestamp.second == 0
    assert milestone.timestamp.microsecond == 0


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
    timestamp = datetime(2024, 10, 24, tzinfo=UTC)

    with pytest.raises(InvalidCompetitionDataError, match=expected_error):
        Milestone(timestamp=timestamp, title=title)
