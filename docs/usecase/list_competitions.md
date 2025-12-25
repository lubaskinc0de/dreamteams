# ListCompetitions

## Purpose

Retrieves paginated list of active competitions with open registration.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `page` | `int` | Page number for pagination | >= 1 |
| `sort_by` | `SortBy` | Sort field (`created_at` or `start_date`) | Enum value |
| `sort_order` | `SortOrder` | Sort direction (`asc` or `desc`) | Enum value |
| `domains` | `list[Domain] \| None` | Filter by technical domains | Optional |
| `participant_type` | `ParticipantType \| None` | Filter by participation type | Optional enum value |
| `team_size` | `TeamSizeRange \| None` | Filter by team size range | Optional, value object validation |
| `format` | `CompetitionFormat \| None` | Filter by competition format | Optional enum value |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `competitions` | `list[CompetitionListItem]` | List of competitions |
| `total` | `int` | Total count of competitions |
| `page` | `int` | Current page number |

### CompetitionListItem

| Field | Type | Description |
|-------|------|-------------|
| `id` | `CompetitionId` | Competition identifier |
| `organizer_id` | `OrganizerId` | Competition organizer identifier |
| `title` | `str` | Competition title |
| `banner` | `Banner \| None` | Competition banner |
| `description` | `str` | Competition description |
| `schedule` | `CompetitionSchedule` | Competition and registration dates |
| `participant_limits` | `ParticipantLimits` | Min/max participant count |
| `domains` | `list[Domain]` | Competition technical domains |
| `participant_type` | `ParticipantType` | Individual or team participation |
| `venue` | `CompetitionVenue` | Competition format and location |
| `team_size` | `TeamSizeRange` | Min/max team size |
| `created_at` | `datetime` | Creation timestamp |

## Business Rules

1. Any user can list competitions
2. Only non-archived competitions are shown
3. Only competitions with open registration are shown (current date between `registration_start` and `registration_end`)
4. Results are sorted by `sort_by` field in `sort_order` direction
5. `team_size` filter shows competitions where ranges overlap with specified range
6. Filters are optional and can be combined

## Error Cases

No specific error cases. Empty list returned if no competitions match criteria.
