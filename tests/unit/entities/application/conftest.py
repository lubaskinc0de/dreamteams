import pytest
from faker import Faker

from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.participant.vo.age import Age
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill, SkillLevel
from dreamteams.entities.user import ExperienceLevel, Participant
from tests.unit.conftest import NOW


@pytest.fixture
def participant(faker: Faker) -> Participant:
    """Standalone Participant entity."""
    return Participant(
        id=faker.uuid4(cast_to=None),
        user_id=faker.uuid4(cast_to=None),
        full_name=faker.name(),
        bio=faker.text(),
        skills=[ParticipantSkill(name="Python", level=SkillLevel.ADVANCED)],
        experience_level=ExperienceLevel.MID,
        preferred_domains=[Domain.BACKEND],
        contacts=[ParticipantContact(title="GitHub", url=faker.url())],
        participant_type=ParticipantType.STUDENT,
        age=Age(20),
        created_at=NOW,
        updated_at=NOW,
    )
