# ReadCompetition

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
| `tags` | `list[CompetitionTag]` | Search tags attached to the competition |
| `tracks` | `list[CompetitionTrack]` | Tracks participants can apply to |
| `participant_type` | `ParticipantType` | Participant type |
| `venue` | `CompetitionVenue` | Format and location |
| `team_size` | `TeamSizeRange` | Team size range |
| `milestones` | `list[Milestone]` | Competition milestones |
| `created_at` | `datetime` | Creation timestamp |

## Business Rules

1. Competition must not be archived
2. Competition registration must be active
