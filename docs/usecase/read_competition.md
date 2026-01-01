# ReadCompetition

## Purpose

Retrieves full competition information by identifier.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `id` | `CompetitionId` | Competition identifier |
| `organizer_id` | `OrganizerId` | Competition organizer identifier |
| `title` | `str` | Competition title |
| `banner` | `Banner \| None` | Competition banner |
| `description` | `str` | Competition description |
| `schedule` | `CompetitionSchedule` | Competition and registration dates |
| `participant_limits` | `ParticipantLimits` | Min/max participant count |
| `domains` | `list[Domain]` | Competition technical domains |
| `participant_type` | `ParticipantType` | Individual or team participation |
| `venue` | `CompetitionVenue` | Competition format and location |
| `team_size` | `TeamSizeRange` | Min/max team size |
| `is_archived` | `bool` | Archive status |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `datetime` | Last update timestamp |

## Business Rules

1. Only organizer who created competition can view it

## Error Cases

- `AccessDeniedError` — organizer is not competition creator
- `CompetitionNotFoundError` — competition not found
