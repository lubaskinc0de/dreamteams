# ReadCompetition

**Actor**: Participant — see [manage_competitions/read_competition.md](../manage_competitions/read_competition.md) for the organizer variant.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `id` | `CompetitionId` | Competition identifier |
| `organizer_id` | `OrganizerId` | Organizer identifier |
| `title` | `str` | Competition title |
| `banner` | `Banner \| None` | Competition banner |
| `description` | `str` | Competition description |
| `schedule` | `CompetitionSchedule` | Registration and event dates |
| `participant_limits` | `ParticipantLimits` | Max participants |
| `domains` | `list[Domain]` | Technical domains |
| `participant_type` | `ParticipantType` | Participant type |
| `venue` | `CompetitionVenue` | Format and location |
| `team_size` | `TeamSizeRange \| None` | Team size range |
| `milestones` | `list[Milestone]` | Competition milestones |
| `auto_accept` | `bool` | Auto-accept applications |
| `is_archived` | `bool` | Archive status |
| `members_count` | `int` | Number of accepted participants |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `datetime` | Last update timestamp |

## Business Rules

1. User must have a Participant profile (`ACCESS_DENIED`)
2. Competition must exist (`COMPETITION_NOT_FOUND`)
