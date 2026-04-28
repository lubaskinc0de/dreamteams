# ChangeCompetitionArchiveStatus

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |
| `is_archived` | `bool` | Archive status | Boolean |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Only organizer who created competition can change archive status.
2. `updated_at` is automatically set to current time.
3. General information, schedule, and team size are not changed by this interactor.
