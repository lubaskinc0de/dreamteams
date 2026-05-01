from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.application.common.dto.participant_contact import ParticipantContactForm
from dreamteams.application.common.dto.participant_skill import ParticipantSkillForm
from dreamteams.application.manage_profile.update_participant import UpdateParticipantForm
from dreamteams.application.register_user.register_participant import ParticipantForm
from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.participant.participant_skill import SkillLevel


def _bio() -> str | None:
    faker = ParticipantFormFactory.__faker__
    if faker.boolean():
        return None
    return faker.sentence(nb_words=5)[:500]


def _skills() -> list[ParticipantSkillForm]:
    """Generate random skills with unique names."""
    faker = ParticipantFormFactory.__faker__
    count = faker.random_int(min=0, max=10)
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
    count = faker.random_int(min=0, max=10)
    return [
        ParticipantContactForm(
            title=f"{faker.word()}-{i}",
            value=f"https://contact-{i}-{faker.lexify('????')}.example.com/",
        )
        for i in range(count)
    ]


def _participant_type() -> ParticipantType:
    return ParticipantFormFactory.__random__.choice([ParticipantType.SCHOOLCHILD, ParticipantType.STUDENT])


def _age() -> int:
    return ParticipantFormFactory.__faker__.random_int(min=0, max=150)


class ParticipantFormFactory(ModelFactory[ParticipantForm]):
    """Factory of ParticipantForm models."""

    __model__ = ParticipantForm
    email: str | None = None
    bio = _bio
    skills = _skills
    contacts = _contacts
    participant_type = _participant_type
    age = _age


class UpdateParticipantFormFactory(ModelFactory[UpdateParticipantForm]):
    """Factory of UpdateParticipantForm models."""

    __model__ = UpdateParticipantForm
    bio = _bio
    skills = _skills
    contacts = _contacts
    participant_type = _participant_type
    age = _age
