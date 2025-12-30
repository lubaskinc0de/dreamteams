import pytest
from faker import Faker

from dreamteams.entities.competition import CompetitionFormat, CompetitionVenue
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


def test_create_online_without_location() -> None:
    """Test creating online venue without location."""
    venue = CompetitionVenue(format=CompetitionFormat.ONLINE, location=None)

    assert venue.format == CompetitionFormat.ONLINE
    assert venue.location is None


@pytest.mark.parametrize(
    "format_type",
    [
        CompetitionFormat.ONLINE,
        CompetitionFormat.OFFLINE,
        CompetitionFormat.HYBRID,
    ],
)
def test_create_with_location(faker: Faker, format_type: CompetitionFormat) -> None:
    """Test creating venue with location."""
    location = faker.address()

    venue = CompetitionVenue(format=format_type, location=location)

    assert venue.format == format_type
    assert venue.location == location


@pytest.mark.parametrize(
    ("format_type", "location"),
    [
        (CompetitionFormat.OFFLINE, None),
        (CompetitionFormat.HYBRID, None),
        (CompetitionFormat.OFFLINE, ""),
        (CompetitionFormat.HYBRID, ""),
        (CompetitionFormat.OFFLINE, "   "),
        (CompetitionFormat.HYBRID, "   "),
    ],
)
def test_create_with_invalid_location_raises_error(format_type: CompetitionFormat, location: str | None) -> None:
    """Test that offline/hybrid formats require non-empty location."""
    with pytest.raises(InvalidCompetitionDataError, match="Location is required for offline or hybrid format"):
        CompetitionVenue(format=format_type, location=location)
