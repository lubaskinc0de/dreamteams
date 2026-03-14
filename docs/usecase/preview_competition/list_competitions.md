# ListCompetitions

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `page` | `int` | Page number for pagination | Positive integer |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[CompetitionModel]` | List of competitions |
| `total` | `int` | Total number of competitions |
| `page` | `int` | Current page number |

### CompetitionModel

| Field | Type | Description |
|-------|------|-------------|
| `id` | `CompetitionId` | Competition identifier |
| `organizer` | `PreviewOrganizerModel` | Organizer information |
| `title` | `str` | Competition title |
| `banner` | `Banner \| None` | Competition banner |
| `description` | `str` | Competition description |
| `schedule` | `CompetitionSchedule` | Registration and event dates |
| `participant_limits` | `ParticipantLimits` | Min/max participants |
| `domains` | `list[Domain]` | Technical domains |
| `participant_type` | `ParticipantType` | Participant type |
| `venue` | `CompetitionVenue` | Format and location |
| `team_size` | `TeamSizeRange` | Team size range |
| `milestones` | `list[Milestone]` | Competition milestones |
| `auto_accept` | `bool` | Auto-accept applications |
| `created_at` | `datetime` | Creation timestamp |

### PreviewOrganizerModel

| Field | Type | Description |
|-------|------|-------------|
| `id` | `OrganizerId` | Organizer identifier |
| `name` | `str` | Organizer name |
| `avatar_url` | `str \| None` | Organizer avatar URL |

## Business Rules

1. Only non-archived competitions are visible
2. Only competitions with active registration are visible
3. Results are sorted by `created_at` descending
4. Returns empty list if no competitions match criteria
