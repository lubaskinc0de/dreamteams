import pytest
from faker import Faker

from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill, SkillLevel
from dreamteams.entities.user import ExperienceLevel, Participant, User
from tests.unit.conftest import NOW


@pytest.fixture
def participant_user(faker: Faker) -> User:
    """User with participant role attached."""
    user_id = faker.uuid4(cast_to=None)
    participant_id = faker.uuid4(cast_to=None)

    user = User(id=user_id, organizer=None)

    participant = Participant(
        id=participant_id,
        user_id=user_id,
        full_name=faker.name(),
        avatar_url=None,
        bio=faker.text(),
        skills=[ParticipantSkill(name="Python", level=SkillLevel.ADVANCED)],
        experience_level=ExperienceLevel.MID,
        preferred_domains=[Domain.BACKEND],
        contacts=[ParticipantContact(title="GitHub", url=faker.url())],
        participant_type=ParticipantType.STUDENT,
        created_at=NOW,
        updated_at=NOW,
    )

    user.participant = participant
    return user
