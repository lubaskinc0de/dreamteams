# ParticipantSkills

## Purpose

Validated collection of participant [ParticipantSkill](participant-skill.md) value objects.

## Business Rules

1. Empty collections are allowed.
2. Skill names must be unique.

## Possible Errors

- `InvalidParticipantDataError` — when two skills share the same name.
