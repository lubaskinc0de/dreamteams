from datetime import UTC, datetime

import pytest

from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.vo.milestones import CompetitionMilestones
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


def test_empty_milestones_list_is_accepted() -> None:
    """CompetitionMilestones accepts an empty list."""
    ms = CompetitionMilestones([])

    assert ms == []


def test_single_milestone_is_accepted() -> None:
    """CompetitionMilestones accepts a single milestone."""
    milestone = Milestone(
        title="Registration opens",
        timestamp=datetime(2026, 5, 1, tzinfo=UTC),
    )

    ms = CompetitionMilestones([milestone])

    assert len(ms) == 1


def test_duplicate_timestamps_are_rejected() -> None:
    """CompetitionMilestones raises InvalidCompetitionDataError when two milestones share a timestamp."""
    timestamp = datetime(2026, 5, 1, tzinfo=UTC)

    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamps must be unique"):
        CompetitionMilestones(
            [
                Milestone(title="Registration opens", timestamp=timestamp),
                Milestone(title="Registration closes", timestamp=timestamp),
            ],
        )
