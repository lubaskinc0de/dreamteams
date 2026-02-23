# ParticipantSkill (Value Object)

## Purpose

Represents a professional skill or technology that a participant can list in their profile.

## Attributes

| Attribute | Type         | Description                                                  |
| --------- | ------------ | ------------------------------------------------------------ |
| `name`    | `str`        | Name of the skill (e.g., "Python", "UI/UX Design", "DevOps") |
| `level`   | `SkillLevel` | Proficiency level in this skill                              |

# SkillLevel (Enum)

| Value          | Description                                            |
| -------------- | ------------------------------------------------------ |
| `BEGINNER`     | Basic understanding, can perform tasks with guidance   |
| `INTERMEDIATE` | Comfortable with core concepts, can work independently |
| `ADVANCED`     | Deep knowledge, can mentor others                      |
| `EXPERT`       | Mastery level, can design and lead in this area        |


## Business Rules

1. `name` must be non-empty and trimmed.
2. Duplicate skills (by `name`) are not allowed within a participant's skill list.
