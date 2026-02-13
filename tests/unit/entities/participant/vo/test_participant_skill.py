import pytest

from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill, SkillLevel


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        "\t\n",
    ],
)
def test_skill_name_is_not_empty(name: str) -> None:
    """Test that empty or whitespace-only skill name raise error."""
    with pytest.raises(InvalidParticipantDataError, match="Skill name must not be empty"):
        ParticipantSkill(name=name, level=SkillLevel.BEGINNER)
