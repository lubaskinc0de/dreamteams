# CreateCompetition

## Purpose

Creates a new competition by organizer.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `title` | `str` | Competition title | Max 200 characters |
| `description` | `str` | Competition description | Non-empty |
| `schedule` | `CompetitionSchedule` | Competition and registration dates | Value object validation |
| `participant_limits` | `ParticipantLimits` | Min/max participant count | Value object validation |
| `domains` | `list[Domain]` | Competition technical domains | Non-empty list |
| `participant_type` | `ParticipantType` | Individual or team participation | Enum value |
| `venue` | `CompetitionVenue` | Competition format and location | Value object validation |
| `team_size` | `TeamSizeRange` | Min/max team size | Value object validation |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `competition_id` | `CompetitionId` | Created competition identifier |

## Business Rules

1. Only user with organizer role can create competition
2. Competition is created as archived (`is_archived = True`)
3. Banner is set to `None` on creation
4. `id`, `created_at`, `updated_at` are generated automatically
5. `organizer_id` is set to current authenticated organizer
6. All validation rules from `CompetitionSchedule`, `CompetitionVenue`, `ParticipantLimits`, `TeamSizeRange` apply

## Error Cases

- `AccessDeniedError` — user does not have organizer role
- `InvalidCompetitionDataError` — validation failed for schedule, venue, limits or team size
