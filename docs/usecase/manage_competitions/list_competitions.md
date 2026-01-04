# ListCompetitions

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `page` | `int` | Page number for pagination | Positive integer |
| `sort_by` | `str` | Field to sort by | Must be one of `created_at`, `title`, `registration_start`, `team_formation_start` |
| `sort_order` | `str` | Sort order | `asc` or `desc` |
| `is_archived` | `bool` | Is archived | `1` or `0` |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[CompetitionModel]` | List of competitions |
| `total` | `int` | Total number of competitions |
| `page` | `int` | Current page number |

### CompetitionModel

| Field | Type | Description |
|-------|------|-------------|
| `id` | `CompetitionId` | Competition identifier |
| `organizer_id` | `OrganizerId` | Organizer identifier |
| `title` | `str` | Competition title |
| `banner` | `Banner \| None` | Competition banner |
| `description` | `str` | Competition description |
| `schedule` | `CompetitionSchedule` | Registration and event dates |
| `participant_limits` | `ParticipantLimits` | Min/max participants |
| `domains` | `list[Domain]` | Technical domains |
| `participant_type` | `ParticipantType` | Participant type |
| `venue` | `CompetitionVenue` | Format and location |
| `team_size` | `TeamSizeRange` | Team size range |
| `milestones` | `list[Milestone]` | Competition milestones |
| `is_archived` | `bool` | Archive status |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `datetime` | Last update timestamp |

## Business Rules

1. Only competitions created by organizer are visible

## Possible Errors

No specific errors. Returns empty list if organizer has no competitions.
