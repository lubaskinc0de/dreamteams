# Participant

## Purpose

Represents a participant (physical person) registered on the platform to take part in hackathons, olympiads, and to find or form teams. The Participant is a role attached to a User and contains profile information, skills, participation history, and preferences.

## Attributes

| Attribute           | Type                   | Description                                               |
| ------------------- | ---------------------- | --------------------------------------------------------- |
| `id`                | `ParticipantId` (UUID) | Unique participant identifier                             |
| `user_id`           | `UserId` (UUID)        | Reference to the associated [User](user.md) account                  |
| `full_name`         | `str`                  | Full name of the participant                              |
| `avatar_url`        | `str \| None`          | URL to the participant's profile picture                  |
| `bio`               | `str`                  | Short biography or description                            |
| `skills`            | `list[`[`ParticipantSkill`](../value-objects/participant-skill.md)`]`          | List of professional skills                               |
| `experience_level`  | [`ExperienceLevel`](#experiencelevel-enum)      | Level of expertise                                        |
| `preferred_domains` | `list[`[`Domain`](../value-objects/domain.md)`]`         | Preferred IT domains (e.g., Web Dev, AI, Cybersecurity)   |
| `contacts`          | `list[`[`ParticipantContact`](../value-objects/participant-contact.md)`]`        | List of contact links (GitHub, Telegram, portfolio, etc.) |
| `created_at`        | `datetime`             | Timestamp of profile creation                             |
| `updated_at`        | `datetime`             | Timestamp of last profile update                          |

# ExperienceLevel (Enum)

| Value    | Description             |
| -------- | ----------------------- |
| `JUNIOR` | 0–2 years of experience |
| `MID`    | 2–5 years of experience |
| `SENIOR` | 5+ years of experience  |

## Business Rules

1. Each participant must be linked to exactly one user via `user_id`.
2. `skills` list must contain at least one skill.
3. `full_name` cannot be empty or consist only of whitespace.
4. `preferred_domains` cannot be empty.
5. All contacts in `contacts` must be unique by `url`.

# Relationships

```
Participant 1 ──> 1 User
Participant 1 ──> N Skill
Participant 1 ──> N Contact
```
