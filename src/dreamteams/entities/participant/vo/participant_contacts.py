from collections.abc import Iterable

from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact


class ParticipantContacts(list[ParticipantContact]):
    """Validated collection of participant contacts: titles and values must each be unique."""

    def __init__(self, items: Iterable[ParticipantContact] = ()) -> None:
        super().__init__(items)
        titles = [c.title for c in self]
        if len(titles) != len(set(titles)):
            raise InvalidParticipantDataError(message="Contact titles must be unique")
        values = [c.value for c in self]
        if len(values) != len(set(values)):
            raise InvalidParticipantDataError(message="Contact values must be unique")
