from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import HttpUrl

from dreamteams.application.common.dto.participant_contact import ParticipantContactForm
from dreamteams.application.common.dto.participant_skill import ParticipantSkillForm
from dreamteams.application.register.register_participant import ParticipantForm
from dreamteams.entities.participant.vo.participant_skill import SkillLevel


def _skills() -> list[ParticipantSkillForm]:
    """Generate random skills with random levels."""
    faker = ParticipantFormFactory.__faker__
    return [
        ParticipantSkillForm(
            name=faker.word(),
            level=faker.random_element(list(SkillLevel)),
        )
        for _ in range(faker.random_int(min=1, max=10))
    ]


def _contacts() -> list[ParticipantContactForm]:
    """Generate random contacts URLs."""
    faker = ParticipantFormFactory.__faker__
    return [
        ParticipantContactForm(
            title=faker.word(),
            url=HttpUrl(faker.url()),
        )
        for _ in range(faker.random_int(min=1, max=10))
    ]


class ParticipantFormFactory(ModelFactory[ParticipantForm]):
    """Factory of ParticipantForm models."""

    __model__ = ParticipantForm
    skills = _skills
    contacts = _contacts
