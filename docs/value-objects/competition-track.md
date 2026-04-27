# CompetitionTrack

Represents a competition direction/category participants apply to, for example `Mobile Development` or `Backend`.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Track name |

## Rules

1. Name is trimmed.
2. Name must not be empty.
3. An application must reference exactly one track offered by the competition.
