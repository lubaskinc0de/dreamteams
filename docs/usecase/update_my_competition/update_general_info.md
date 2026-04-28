# UpdateCompetitionGeneralInfo

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |
| `title` | `str` | New title | Max 200 characters |
| `description` | `str` | New description | Non-empty |
| `participant_limits` | `ParticipantLimits` | New participant limits | Value object validation |
| `tag_ids` | `list[CompetitionTagId]` | New search tags from the admin-managed catalog | Optional; max 30 |
| `tracks` | `list[CompetitionTrackForm]` | New tracks participants can apply to | Non-empty list; unique names |
| `participant_type` | `ParticipantType` | New participant type | Enum value |
| `venue` | `CompetitionVenue` | New location | Value object validation |
| `milestones` | `list[MilestoneForm] \| None` | Competition milestones | `None` clears milestones; list replaces them |
| `auto_accept` | `bool` | Auto-accept applications | Boolean |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Only organizer who created competition can update it.
2. `updated_at` is automatically set to current time.
3. Schedule, team size, and archive status are not changed by this interactor.
4. Existing tracks are always replaced with the submitted tracks.
5. If milestones are provided, existing milestones are cleared first, then new ones are added.
6. Milestone timestamps must be unique.
7. Every `tag_id` must reference an existing competition tag (`COMPETITION_TAG_NOT_FOUND`).
