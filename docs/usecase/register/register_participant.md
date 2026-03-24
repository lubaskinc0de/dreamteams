# RegisterParticipant

## Purpose
Registers a new participant

## Input
| Field               | Type                      | Description |
|---------------------|---------------------------|-------------|
| `full_name`         | `str`                     | Full name   |
| `bio`               | `str`                     | Short biography or description |
| `skills`            | `list[ParticipantSkill]`  | List of participant skills |
| `experience_level`  | `ExperienceLevel`         | Experience level |
| `preferred_domains` | `list[Domain]`            | List of preferred domains |
| `contacts`          | `list[ParticipantContact]`| List of contacts |

## Output
| Field | Type | Description |
|-------|------|-------------|
| `participant_id` | `ParticipantId` | Created participant identifier |
| `user_id` | `UserId` | Created user identifier |


## Business Rules
1. Full name must not be empty
2. Skills list must not be empty
3. Preferred domains list must not be empty
4. Contact URLs must be unique


## Errors
| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `INVALID_PARTICIPANT_DATA` | 422 | Any validation rule fails |

