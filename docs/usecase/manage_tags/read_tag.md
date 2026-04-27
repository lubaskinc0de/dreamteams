# ReadCompetitionTag

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `tag_id` | `CompetitionTagId` | Tag identifier | UUID format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `id` | `CompetitionTagId` | Tag identifier |
| `value` | `str` | Tag value |

## Business Rules

1. Only admins can read tags through this use case.
2. Unknown tags return `COMPETITION_TAG_NOT_FOUND`.
