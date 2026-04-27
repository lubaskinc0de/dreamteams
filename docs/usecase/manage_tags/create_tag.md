# CreateCompetitionTag

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `value` | `str` | Tag value | 1-100 characters after trimming |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `id` | `CompetitionTagId` | Created tag identifier |
| `value` | `str` | Normalized tag value |

## Business Rules

1. Only admins can create tags.
2. Tag values must be unique case-insensitively (`COMPETITION_TAG_ALREADY_EXISTS`).
