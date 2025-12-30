# Competition

## Purpose

Represents a hackathon or olympiad event created by an organizer.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `CompetitionId` (UUID) | Competition identifier |
| `organizer_id` | `OrganizerId` (UUID) | Reference to organizer who created the competition |
| `title` | `str` | Competition title |
| `banner` | `str \| None` | Banner image URL |
| `description` | `str` | Detailed description of the competition |
| `schedule` | `CompetitionSchedule` | Competition dates and registration period |
| `participant_limits` | `ParticipantLimits` | Min and max participants |
| `domains` | `list[Domain]` | IT domains relevant to this competition |
| `participant_type` | `ParticipantType` | Target participant category |
| `venue` | `CompetitionVenue` | Event format and location |
| `team_size` | `TeamSizeRange` | Min and max team size |
| `is_archived` | `bool` | Whether competition is archived |
| `created_at` | `datetime` | When competition was created |
| `updated_at` | `datetime` | Last update timestamp |

## Value Objects

### CompetitionSchedule
- `competition_start: datetime` - Competition start date
- `competition_end: datetime` - Competition end date
- `registration_start: datetime` - Registration opens
- `registration_end: datetime` - Registration closes
- `team_formation_start: datetime | None` - Team formation period start (optional)
- `team_formation_end: datetime | None` - Team formation period end (optional)
- All datetime values are normalized (seconds and microseconds set to 0)
- Validates:
  - All dates must not be in the past
  - competition_end must be after competition_start
  - registration_end must be after registration_start
  - registration_end must be before or equal to competition_start
  - If team formation period is specified, both start and end must be provided
  - team_formation_start must be after or equal to registration_end
  - team_formation_end must be after team_formation_start
  - team_formation_end must be before or equal to competition_end

### CompetitionVenue
- `format: CompetitionFormat` - Event format (online/offline/hybrid)
- `location: str | None` - Physical location
- Validates: location is required for offline or hybrid format

### ParticipantLimits
- `max: int` - Maximum participants
- `min: int` - Minimum participants
- Validates: max > 0, min ≤ max

### TeamSizeRange
- `max: int` - Maximum team size
- `min: int` - Minimum team size
- Validates: min ≥ 1, max > 0, min ≤ max

## Business Rules

1. Domains list must not be empty
2. Archived competitions (`is_archived=True`) are not visible to participants

## Relationships

```
Competition N ──> 1 Organizer
```

- Each competition belongs to exactly one organizer
- One organizer can create multiple competitions
