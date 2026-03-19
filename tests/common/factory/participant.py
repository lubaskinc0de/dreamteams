from polyfactory.factories.pydantic_factory import ModelFactory

from dreamteams.application.register.register_participant import ParticipantForm
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill, SkillLevel


def _avatar_url() -> str | None:
    """Generate fake participant avatar url."""
    faker = ParticipantFormFactory.__faker__
    return faker.image_url() if faker.boolean() else None


def _skills() -> list[ParticipantSkill]:
    """Generate random skills with random levels."""
    faker = ParticipantFormFactory.__faker__
    return [
        ParticipantSkill(
            name=faker.word(),
            level=faker.random_element(list(SkillLevel)),
        )
        for _ in range(faker.random_int(min=1, max=10))
    ]


def _contacts() -> list[ParticipantContact]:
    """Generate random contacts URLs."""
    faker = ParticipantFormFactory.__faker__
    return [
        ParticipantContact(
            title=faker.word(),
            url=faker.url(),
        )
        for _ in range(faker.random_int(min=1, max=10))
    ]


def _bio() -> str:
    """Generate random bio."""
    faker = ParticipantFormFactory.__faker__
    return faker.text(max_nb_chars=200)


class ParticipantFormFactory(ModelFactory[ParticipantForm]):
    """Factory of ParticipantForm models."""

    __model__ = ParticipantForm
    avatar_url = _avatar_url
    bio = _bio
    skills = _skills
    contacts = _contacts
