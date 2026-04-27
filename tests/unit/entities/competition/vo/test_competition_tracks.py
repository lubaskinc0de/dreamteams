import pytest

from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.entities.competition.vo.tracks import CompetitionTracks
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


def test_empty_constructor_is_accepted_for_collection_initialization() -> None:
    """CompetitionTracks accepts no-argument construction for collection initialization."""
    # Act
    result = CompetitionTracks()

    # Assert
    assert result == []


def test_competition_tracks_are_not_empty() -> None:
    """CompetitionTracks rejects an explicitly empty collection."""
    # Act / Assert
    with pytest.raises(InvalidCompetitionDataError, match="Competition tracks must not be empty"):
        CompetitionTracks([])


def test_duplicate_track_names_are_rejected_case_insensitively() -> None:
    """CompetitionTracks rejects duplicate names case-insensitively."""
    # Arrange
    tracks = [
        CompetitionTrack("Backend"),
        CompetitionTrack("backend"),
    ]

    # Act / Assert
    with pytest.raises(InvalidCompetitionDataError, match="Competition track names must be unique"):
        CompetitionTracks(tracks)
