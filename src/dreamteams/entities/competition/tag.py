from dataclasses import dataclass
from uuid import uuid4

from dreamteams.entities.base import Entity
from dreamteams.entities.common.identifiers import CompetitionTagId
from dreamteams.entities.errors.competition import InvalidCompetitionDataError


@dataclass
class CompetitionTag(Entity):
    """Tag used for competition discovery."""

    id: CompetitionTagId
    value: str

    def __post_init__(self) -> None:
        """Validate and normalize tag value."""
        self.value = self.value.strip()
        if not self.value:
            raise InvalidCompetitionDataError(message="Tag value must not be empty")


def competition_tag_factory(value: str) -> CompetitionTag:
    """Create a new competition tag."""
    return CompetitionTag(id=uuid4(), value=value)
