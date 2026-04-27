import pytest

from dreamteams.entities.errors.participant import InvalidParticipantDataError
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill, SkillLevel
from dreamteams.entities.participant.vo.participant_skills import ParticipantSkills


def test_empty_skills_list_is_accepted() -> None:
    """ParticipantSkills accepts an empty list."""
    skills = ParticipantSkills([])

    assert skills == []


def test_unique_skill_names_are_accepted() -> None:
    """ParticipantSkills accepts skills with unique names."""
    skills = ParticipantSkills(
        [
            ParticipantSkill(name="Python", level=SkillLevel.BEGINNER),
            ParticipantSkill(name="SQL", level=SkillLevel.INTERMEDIATE),
        ],
    )

    assert len(skills) == 2


def test_duplicate_skill_names_are_rejected() -> None:
    """ParticipantSkills rejects duplicate skill names."""
    with pytest.raises(InvalidParticipantDataError, match="Skill names must be unique"):
        ParticipantSkills(
            [
                ParticipantSkill(name="Python", level=SkillLevel.BEGINNER),
                ParticipantSkill(name="Python", level=SkillLevel.EXPERT),
            ],
        )
