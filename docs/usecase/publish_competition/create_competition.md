# CreateCompetition

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `title` | `str` | Competition title | Max 200 characters |
| `description` | `str` | Competition description | Non-empty |
| `schedule` | `CompetitionSchedule` | Registration and event dates | Value object validation |
| `participant_limits` | `ParticipantLimits` | Max participants | Value object validation |
| `tag_ids` | `list[CompetitionTagId]` | Search tags from the admin-managed catalog | Optional; max 30 |
| `tracks` | `list[CompetitionTrackForm]` | Tracks participants can apply to | Non-empty list; unique names |
| `participant_type` | `ParticipantType` | Participant type | Enum value |
| `venue` | `CompetitionVenue` | Format and location | Value object validation |
| `team_size` | `TeamSizeRange \| None` | Team size range | Optional — must be set together with `schedule.team_formation_{start,end}` or both omitted |
| `auto_accept` | `bool` | Auto-accept applications | Default `False` |
| `milestones` | `list[MilestoneForm]` | Competition milestones | Optional, default [] |

### MilestoneForm

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `title` | `str` | Milestone title | Max 50 characters, non-empty |
| `timestamp` | `datetime` | Milestone timestamp | Valid datetime |
| `description` | `str \| None` | Optional free-form context | Max 300 characters |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `competition_id` | `CompetitionId` | Created competition identifier |

## Business Rules

1. Only user with organizer role can create competitions
2. Competition is created as archived (`is_archived = True`)
3. Banner is set to `None`
4. Fields `id`, `created_at`, `updated_at` are generated automatically
5. `organizer_id` is set from current authenticated user
6. All value object validation rules apply
7. If milestones are provided, their timestamps must be unique
8. `auto_accept` defaults to `False`; when `True`, participant applications are accepted immediately
9. `team_size` and `schedule.team_formation_{start,end}` are a paired group — either all three are provided (team competition) or all three are omitted (individual competition). Any mismatch raises `INVALID_COMPETITION_DATA`.
10. Every `tag_id` must reference an existing competition tag (`COMPETITION_TAG_NOT_FOUND`)
