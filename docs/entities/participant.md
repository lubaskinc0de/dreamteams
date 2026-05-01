# Participant

## Purpose

Represents a participant (physical person) registered on the platform to take part in hackathons, olympiads, and to find or form teams. The Participant is a role attached to a User and contains profile information, skills, participation history, and preferences.

## Attributes

| Attribute           | Type                   | Required | Description                                               |
| ------------------- | ---------------------- | -------- | --------------------------------------------------------- |
| `id`                | `ParticipantId` (UUID) | Yes      | Unique participant identifier                             |
| `user_id`           | `UserId` (UUID)        | Yes      | Reference to the associated [User](user.md) account       |
| `full_name`         | `str`                  | Yes      | Full name of the participant                              |
| `participant_type`  | [`ParticipantType`](#participanttype-enum) | Yes | Participant type |
| `age`               | [`Age`](#age-vo)       | Yes      | Age of the participant (0–150)                            |
| `avatar_url`        | `str \| None`          | No       | URL to the participant's profile picture                  |
| `bio`               | `str \| None`          | No       | Short biography or description                            |
| `skills`            | [`ParticipantSkills`](../value-objects/participant-skills.md) | No | Collection of professional skills |
| `experience_level`  | [`ExperienceLevel`](#experiencelevel-enum) `\| None` | No | Level of expertise |
| `contacts`          | [`ParticipantContacts`](../value-objects/participant-contacts.md) | No | Collection of contact values (GitHub, Telegram, portfolio, phone, etc.) |
| `created_at`        | `datetime`             | Yes      | Timestamp of profile creation                             |
| `updated_at`        | `datetime`             | Yes      | Timestamp of last profile update                          |

## Age (VO)

A value object wrapping a participant's age as an integer.

| Constraint | Value |
| ---------- | ----- |
| Minimum    | 0     |
| Maximum    | 150   |

## ParticipantType (Enum)

| Value         | Description        |
| ------------- | ------------------ |
| `SCHOOLCHILD` | School student     |
| `STUDENT`     | University student |

## ExperienceLevel (Enum)

| Value    | Description             |
| -------- | ----------------------- |
| `JUNIOR` | 0–2 years of experience |
| `MID`    | 2–5 years of experience |
| `SENIOR` | 5+ years of experience  |

## Business Rules

1. Each participant must be linked to exactly one user via `user_id`.
2. `full_name` is validated at the application boundary.
3. `participant_type` cannot be `ANY`.
4. Age must be between 0 and 150 inclusive.
5. Skill names in `skills` must be unique.
6. Contacts in `contacts` must be unique by `title`.
7. Contacts in `contacts` must be unique by `value`.
8. Participant create/update request bodies accept at most 15 submitted contacts.
9. During registration, a non-blank auth email is saved as a contact with title `Email`.

## Relationships

```
Participant 1 ──> 1 User
Participant 1 ──> N Skill
Participant 1 ──> N Contact
```
