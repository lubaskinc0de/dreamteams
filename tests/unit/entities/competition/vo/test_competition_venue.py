import pytest
from faker import Faker

from dreamteams.entities.competition.venue import CompetitionFormat, CompetitionVenue
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


def test_create_venue_without_location() -> None:
    """Test creating online venue without location."""
    venue = CompetitionVenue(format=CompetitionFormat.ONLINE, location=None)

    assert venue.format == CompetitionFormat.ONLINE
    assert venue.location is None


@pytest.mark.parametrize(
    "format_type",
    [
        CompetitionFormat.ONLINE,  # Online format can have location (optional)
        CompetitionFormat.OFFLINE,  # Offline format requires location
        CompetitionFormat.HYBRID,  # Hybrid format requires location
    ],
)
def test_create_with_location(faker: Faker, format_type: CompetitionFormat) -> None:
    """Test creating venue with location for any format type."""
    location = faker.address()

    venue = CompetitionVenue(format=format_type, location=location)

    assert venue.format == format_type
    assert venue.location == location


@pytest.mark.parametrize(
    ("location"),
    [
        # Offline format requires non-empty location
        None,
        "",
        "   ",
    ],
)
def test_offline_venue_requires_location(location: str | None) -> None:
    """Test that offline format require non-empty location."""
    with pytest.raises(InvalidCompetitionDataError, match="Location is required for offline or hybrid format"):
        CompetitionVenue(format=CompetitionFormat.OFFLINE, location=location)


@pytest.mark.parametrize(
    ("location"),
    [
        # Hybrid format requires non-empty location
        None,
        "",
        "   ",
    ],
)
def test_hybrid_venue_requires_location(location: str | None) -> None:
    """Test that hybrid format require non-empty location."""
    with pytest.raises(InvalidCompetitionDataError, match="Location is required for offline or hybrid format"):
        CompetitionVenue(format=CompetitionFormat.HYBRID, location=location)
