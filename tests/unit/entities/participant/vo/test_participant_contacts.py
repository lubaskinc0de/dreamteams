import pytest

from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_contacts import ParticipantContacts


def test_empty_contacts_list_is_accepted() -> None:
    """ParticipantContacts accepts an empty list."""
    contacts = ParticipantContacts([])

    assert contacts == []


def test_unique_contacts_are_accepted() -> None:
    """ParticipantContacts accepts contacts with unique titles and values."""
    contacts = ParticipantContacts(
        [
            ParticipantContact(title="Telegram", value="@alice"),
            ParticipantContact(title="Email", value="alice@example.com"),
        ],
    )

    assert len(contacts) == 2


def test_duplicate_contact_titles_are_rejected() -> None:
    """ParticipantContacts rejects duplicate contact titles."""
    with pytest.raises(InvalidParticipantDataError, match="Contact titles must be unique"):
        ParticipantContacts(
            [
                ParticipantContact(title="Telegram", value="@alice"),
                ParticipantContact(title="Telegram", value="@bob"),
            ],
        )


def test_duplicate_contact_values_are_rejected() -> None:
    """ParticipantContacts rejects duplicate contact values."""
    with pytest.raises(InvalidParticipantDataError, match="Contact values must be unique"):
        ParticipantContacts(
            [
                ParticipantContact(title="Telegram", value="@alice"),
                ParticipantContact(title="Discord", value="@alice"),
            ],
        )
