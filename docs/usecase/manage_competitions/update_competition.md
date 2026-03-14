# UpdateCompetition

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |
| `title` | `str` | New title | Max 200 characters |
| `description` | `str` | New description | Non-empty |
| `schedule` | `CompetitionSchedule` | New dates | Value object validation |
| `participant_limits` | `ParticipantLimits` | New participant limits | Value object validation |
| `domains` | `list[Domain]` | New technical domains | Non-empty list |
| `participant_type` | `ParticipantType` | New participant type | Enum value |
| `venue` | `CompetitionVenue` | New location | Value object validation |
| `team_size` | `TeamSizeRange` | New team size | Value object validation |
| `milestones` | `list[MilestoneForm]` | Competition milestones | Can be empty list |
| `auto_accept` | `bool` | Auto-accept applications | Boolean |
| `is_archived` | `bool` | Archive status | Boolean |

### MilestoneForm

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `title` | `str` | Milestone title | Max 50 characters, non-empty |
| `timestamp` | `datetime` | Milestone timestamp | Valid datetime |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Only organizer who created competition can update it
2. `updated_at` is automatically set to current time
3. All value object validation rules apply
4. If milestones are provided, existing ones are cleared first, then new ones added
5. Milestone timestamps must be unique
