# ExploreCompetitions

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `page` | `int` | Page number for pagination | Positive integer (default `1`) |
| `sort_by` | `str` | Sort field | `most_popular` (default) or `newest` |
| `search` | `str \| null` | Search on competition title and attached tag values (trigram similarity) | Optional |
| `min_team_size` | `int \| null` | Participant's desired minimum team size | Positive integer; optional |
| `max_team_size` | `int \| null` | Participant's desired maximum team size | Positive integer; optional |
| `auto_accept` | `bool \| null` | Exact match on competition's `auto_accept` | Optional |
| `tag_ids` | `list[CompetitionTagId] \| null` | Match competitions whose tags overlap with any of these | Optional |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[ExploreCompetitionModel]` | Page of competitions the participant can submit to |
| `total` | `int` | Total number of matching competitions |
| `page` | `int` | Current page number |

### ExploreCompetitionModel

| Field | Type | Description |
|-------|------|-------------|
| `id` | `CompetitionId` | Competition identifier |
| `organizer` | `ExploreOrganizerModel` | Organizer summary (id, name, avatar_url) |
| `title` | `str` | Competition title |
| `banner` | `Banner \| None` | Competition banner |
| `description` | `str` | Competition description |
| `schedule` | `CompetitionSchedule` | Registration and event dates |
| `participant_limits` | `ParticipantLimits` | Max participants |
| `tags` | `list[CompetitionTag]` | Search tags attached to the competition |
| `tracks` | `list[CompetitionTrack]` | Tracks participants can apply to |
| `participant_type` | `ParticipantType` | Participant type requirement |
| `venue` | `CompetitionVenue` | Format and location |
| `team_size` | `TeamSizeRange` | Team size range |
| `milestones` | `list[Milestone]` | Competition milestones |
| `auto_accept` | `bool` | Auto-accept applications |
| `members_count` | `int` | Number of accepted participants so far |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `datetime` | Last update timestamp |

## Business Rules

1. User must have a Participant profile (`ACCESS_DENIED`)
2. Only non-archived competitions in an active registration window are returned
3. The participant has not already submitted an application to the competition
4. The competition's `participant_type` is `ANY` or matches the participant's own type
5. `members_count` (number of accepted applications) is strictly below `participant_limits.max`
6. `min_team_size` / `max_team_size`, if provided, must overlap with the competition's own team-size range
7. `auto_accept`, if provided, must exactly match the competition's value
8. `tag_ids`, if provided, must overlap with the competition's tags
9. `search`, if provided, uses trigram similarity against the title and attached tag values
10. `most_popular` (default) sorts by `members_count` descending; `newest` sorts by `created_at` descending
11. Stable ordering is guaranteed via `id` as the final tiebreaker
