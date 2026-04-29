# Competition

## Purpose

Represents a hackathon or olympiad event created by an organizer.

## Attributes

| Attribute            | Type                   | Description                                        |
| -------------------- | ---------------------- | -------------------------------------------------- |
| `id`                 | `CompetitionId` (UUID) | Competition identifier                             |
| `organizer_id`       | `OrganizerId` (UUID)   | Reference to [Organizer](organizer.md) who created the competition |
| `title`              | `str`                  | Competition title                                  |
| `banner`             | `str \| None`          | Banner image URL                                   |
| `description`        | `str`                  | Detailed description of the competition            |
| `schedule`           | [`CompetitionSchedule`](../value-objects/competition-schedule.md)  | Competition dates and registration period          |
| `participant_limits` | [`ParticipantLimits`](../value-objects/participant-limits.md)    | Max participants                                    |
| `tags`               | `list[`[`CompetitionTag`](competition-tag.md)`]`         | Search tags used for fast competition discovery    |
| `tracks`             | [`CompetitionTracks`](../value-objects/competition-tracks.md) | Competition directions/categories participants can apply to |
| `participant_type`   | [`ParticipantType`](../value-objects/participant-type.md)      | Target participant category                        |
| `venue`              | [`CompetitionVenue`](../value-objects/competition-venue.md)     | Event format and location                          |
| `team_size`          | [`TeamSizeRange`](../value-objects/team-size-range.md) `\| None` | Min and max team size (optional — paired with schedule.team_formation_*) |
| `milestones`         | [`CompetitionMilestones`](../value-objects/competition-milestones.md) | Custom timeline milestones                         |
| `auto_accept`        | `bool`                 | Auto-accept applications (default: `False`)        |
| `is_archived`        | `bool`                 | Whether competition is archived                    |
| `created_at`         | `datetime`             | When competition was created                       |
| `updated_at`         | `datetime`             | Last update timestamp                              |

## Business Rules

1. Tracks list must not be empty
2. Track names must be unique within a competition
3. Competition tags must be unique by ID and value within a competition
4. A competition can reference at most 30 tags at the application boundary
5. Milestone timestamps must be unique within a competition
6. Description non-empty validation happens at the application boundary
7. Only the organizer who created the competition can read, update, or delete it
8. New competitions are created with `is_archived=True` by default
9. Archived competitions are not visible to participants
10. `team_size` and `schedule.team_formation_{start,end}` are paired: either all three are set (team competition) or all three are `None` (individual competition). Setting one side without the other raises `InvalidCompetitionDataError`.

## Relationships

```
Competition N ──> 1 Organizer
Competition 1 ──> N Milestone
Competition N ──> N CompetitionTag
Competition 1 ──> N CompetitionTrack
```

-   Each competition belongs to exactly one organizer
-   One organizer can create multiple competitions
-   Each competition can have multiple milestones (0..N)
-   Milestones are deleted when their competition is deleted (cascade)
-   Each competition can reference multiple catalog tags (0..30 at the API boundary)
-   Each competition stores its own tracks in a separate table; tracks are deleted with the competition
