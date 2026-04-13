from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import HttpUrl

from dreamteams.application.common.dto.participant_contact import ParticipantContactForm
from dreamteams.application.common.dto.participant_skill import ParticipantSkillForm
from dreamteams.application.register.register_participant import ParticipantForm
from dreamteams.entities.participant.vo.participant_skill import SkillLevel


def _skills() -> list[ParticipantSkillForm]:
    """Generate random skills with unique names."""
    faker = ParticipantFormFactory.__faker__
    count = faker.random_int(min=1, max=10)
    return [
        ParticipantSkillForm(
            name=f"{faker.word()}-{i}",
            level=faker.random_element(list(SkillLevel)),
        )
        for i in range(count)
    ]


def _contacts() -> list[ParticipantContactForm]:
    """Generate random contacts with unique titles and URLs."""
    faker = ParticipantFormFactory.__faker__
    count = faker.random_int(min=1, max=10)
    return [
        ParticipantContactForm(
            title=f"{faker.word()}-{i}",
            url=HttpUrl(f"https://contact-{i}-{faker.lexify('????')}.example.com/"),
        )
        for i in range(count)
    ]


class ParticipantFormFactory(ModelFactory[ParticipantForm]):
    """Factory of ParticipantForm models."""

    __model__ = ParticipantForm
    skills = _skills
    contacts = _contacts
