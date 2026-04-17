# RegisterParticipant

## Purpose
Registers a new participant

## Input
| Field               | Type                      | Required | Description |
|---------------------|---------------------------|----------|-------------|
| `full_name`         | `str`                     | Yes      | Full name   |
| `participant_type`  | `ParticipantType`         | Yes      | Participant type (`SCHOOLCHILD` or `STUDENT`) |
| `age`               | `int`                     | Yes      | Age (0–150) |
| `bio`               | `str \| None`             | No       | Short biography or description |
| `skills`            | `list[ParticipantSkill]`  | No       | List of participant skills (default: empty) |
| `experience_level`  | `ExperienceLevel \| None` | No       | Experience level |
| `preferred_domains` | `list[Domain]`            | No       | List of preferred domains (default: empty) |
| `contacts`          | `list[ParticipantContact]`| No       | List of contacts (default: empty) |


## Output
| Field | Type | Description |
|-------|------|-------------|
| `participant_id` | `ParticipantId` | Created participant identifier |
| `user_id` | `UserId` | Created user identifier |


## Business Rules
1. Full name must not be empty
2. `participant_type` cannot be `ANY`
3. Age must be between 0 and 150 inclusive
4. Skill names must be unique within the skills list
5. Contact titles must be unique within the contacts list
6. Contact URLs must be unique within the contacts list


## Errors
| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `INVALID_PARTICIPANT_DATA` | 422 | Any validation rule fails |
