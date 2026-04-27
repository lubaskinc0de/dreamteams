# DeleteCompetitionTag

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `tag_id` | `CompetitionTagId` | Tag identifier | UUID format |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Only admins can delete tags.
2. Unknown tags return `COMPETITION_TAG_NOT_FOUND`.
3. Deleting a tag removes competition links through database cascade.
