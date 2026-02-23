import pytest

from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact


@pytest.mark.parametrize(
    "title",
    [
        "",
        " ",
        ("\t\n"),
    ],
)
def test_title_is_not_empty(title: str) -> None:
    """Test that empty or whitespace-only title raise error."""
    with pytest.raises(InvalidParticipantDataError, match="Contact title not must be empty"):
        ParticipantContact(title=title, url="https://dreamteams.com")
