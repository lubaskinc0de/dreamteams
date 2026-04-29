from polyfactory.factories import DataclassFactory

from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.participant.age import Age
from dreamteams.entities.participant.participant_contact import ParticipantContact
from dreamteams.entities.participant.participant_contacts import ParticipantContacts
from dreamteams.entities.participant.participant_skill import ParticipantSkill, SkillLevel
from dreamteams.entities.participant.participant_skills import ParticipantSkills
from dreamteams.entities.user import ParticipantData


def _skills() -> ParticipantSkills:
    faker = ParticipantDataFactory.__faker__
    count = faker.random_int(min=0, max=5)

    return ParticipantSkills(
        [
            ParticipantSkill(name=f"{faker.word()}-{i}", level=faker.random_element(list(SkillLevel)))
            for i in range(count)
        ],
    )


def _contacts() -> ParticipantContacts:
    faker = ParticipantDataFactory.__faker__
    count = faker.random_int(min=0, max=5)

    return ParticipantContacts(
        [
            ParticipantContact(
                title=f"{faker.word()}-{i}",
                value=f"https://contact-{i}-{faker.lexify('????')}.example.com/",
            )
            for i in range(count)
        ],
    )


def _participant_type() -> ParticipantType:
    return ParticipantDataFactory.__random__.choice([ParticipantType.SCHOOLCHILD, ParticipantType.STUDENT])


def _age() -> Age:
    return Age(ParticipantDataFactory.__faker__.random_int(min=0, max=150))


class ParticipantDataFactory(DataclassFactory[ParticipantData]):
    """Factory of ParticipantData DTOs (fed into the domain ``participant_factory``)."""

    __model__ = ParticipantData

    skills = _skills
    contacts = _contacts
    participant_type = _participant_type
    age = _age
