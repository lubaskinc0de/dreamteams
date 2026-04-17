# UpdateParticipant

## Purpose

Updates the participant profile of the currently authenticated user.

## Input

| Field               | Type                      | Required | Description |
|---------------------|---------------------------|----------|-------------|
| `full_name`         | `str`                     | Yes      | Full name (1–70 characters) |
| `participant_type`  | `ParticipantType`         | Yes      | Participant type (`SCHOOLCHILD` or `STUDENT`) |
| `age`               | `int`                     | Yes      | Age (0–150) |
| `bio`               | `str \| None`             | No       | Short biography or description (max 500 characters) |
| `skills`            | `list[ParticipantSkill]`  | No       | List of participant skills (default: empty) |
| `experience_level`  | `ExperienceLevel \| None` | No       | Experience level |
| `preferred_domains` | `list[Domain]`            | No       | List of preferred domains (default: empty) |
| `contacts`          | `list[ParticipantContact]`| No       | List of contacts (default: empty) |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Full name must not be empty
2. `participant_type` cannot be `ANY`
3. Age must be between 0 and 150 inclusive
4. Skill names must be unique within the skills list
5. Contact titles must be unique within the contacts list
6. Contact URLs must be unique within the contacts list
7. `avatar_url` is preserved from the existing profile (not updatable via this use case)

## Errors

| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `PARTICIPANT_NOT_FOUND` | 404 | Authenticated user has no participant role |
| `INVALID_PARTICIPANT_DATA` | 400 | Any validation rule fails |
| `UNAUTHORIZED` | 401 | User is not authenticated |
