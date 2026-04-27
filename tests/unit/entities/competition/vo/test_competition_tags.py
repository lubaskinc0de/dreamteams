from uuid import uuid4

import pytest

from dreamteams.entities.competition.tag import CompetitionTag
from dreamteams.entities.competition.vo.tags import CompetitionTags
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


def test_empty_tags_list_is_accepted() -> None:
    """CompetitionTags accepts an empty collection."""
    # Act
    result = CompetitionTags()

    # Assert
    assert result == []


def test_duplicate_tag_ids_are_rejected() -> None:
    """CompetitionTags rejects duplicate tag IDs."""
    # Arrange
    tag_id = uuid4()
    tags = [
        CompetitionTag(id=tag_id, value="Python"),
        CompetitionTag(id=tag_id, value="Backend"),
    ]

    # Act / Assert
    with pytest.raises(InvalidCompetitionDataError, match="Competition tags must be unique"):
        CompetitionTags(tags)


def test_duplicate_tag_values_are_rejected_case_insensitively() -> None:
    """CompetitionTags rejects duplicate tag values case-insensitively."""
    # Arrange
    tags = [
        CompetitionTag(id=uuid4(), value="Python"),
        CompetitionTag(id=uuid4(), value="python"),
    ]

    # Act / Assert
    with pytest.raises(InvalidCompetitionDataError, match="Competition tags must be unique"):
        CompetitionTags(tags)
