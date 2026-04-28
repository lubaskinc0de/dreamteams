# DeleteCompetition

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Only organizer who created competition can delete it
