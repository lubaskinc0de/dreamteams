# Competition

## Purpose

Represents a hackathon or olympiad event created by an organizer.

## Attributes

| Attribute            | Type                   | Description                                        |
| -------------------- | ---------------------- | -------------------------------------------------- |
| `id`                 | `CompetitionId` (UUID) | Competition identifier                             |
| `organizer_id`       | `OrganizerId` (UUID)   | Reference to organizer who created the competition |
| `title`              | `str`                  | Competition title                                  |
| `banner`             | `str \| None`          | Banner image URL                                   |
| `description`        | `str`                  | Detailed description of the competition            |
| `schedule`           | `CompetitionSchedule`  | Competition dates and registration period          |
| `participant_limits` | `ParticipantLimits`    | Min and max participants                           |
| `domains`            | `list[Domain]`         | IT domains relevant to this competition            |
| `participant_type`   | `ParticipantType`      | Target participant category                        |
| `venue`              | `CompetitionVenue`     | Event format and location                          |
| `team_size`          | `TeamSizeRange`        | Min and max team size                              |
| `milestones`         | `list[Milestone]`      | Custom timeline milestones                         |
| `auto_accept`        | `bool`                 | Auto-accept applications (default: `False`)        |
| `is_archived`        | `bool`                 | Whether competition is archived                    |
| `created_at`         | `datetime`             | When competition was created                       |
| `updated_at`         | `datetime`             | Last update timestamp                              |

## Business Rules

1. Domains list must not be empty
2. Milestone timestamps must be unique within a competition
3. Description must not be empty or whitespace-only
4. Only the organizer who created the competition can read, update, or delete it
5. New competitions are created with `is_archived=True` by default
6. Archived competitions are not visible to participants

## Relationships

```
Competition N ──> 1 Organizer
Competition 1 ──> N Milestone
```

-   Each competition belongs to exactly one organizer
-   One organizer can create multiple competitions
-   Each competition can have multiple milestones (0..N)
-   Milestones are deleted when their competition is deleted (cascade)
