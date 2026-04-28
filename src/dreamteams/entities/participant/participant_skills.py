from collections.abc import Iterable

from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.participant_skill import ParticipantSkill


class ParticipantSkills(list[ParticipantSkill]):
    """Validated collection of participant skills — skill names must be unique."""

    def __init__(self, items: Iterable[ParticipantSkill] = ()) -> None:
        super().__init__(items)
        names = [s.name for s in self]
        if len(names) != len(set(names)):
            raise InvalidParticipantDataError(message="Skill names must be unique")
