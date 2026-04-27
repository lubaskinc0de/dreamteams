# ListCompetitionTags

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `page` | `int` | Page number | Positive integer, default `1` |
| `search` | `str \| None` | Case-insensitive substring search by tag value | Optional |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[CompetitionTag]` | Current page of tags |
| `total` | `int` | Total matching tags |
| `page` | `int` | Current page |

## Business Rules

1. Only admins can list tags through this use case.
2. Results are ordered by lowercased tag value and then ID.
