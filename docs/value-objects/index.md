# Value Objects

Immutable types used within entities. Value objects have no identity — two instances with equal fields are considered equal.

## Competition

| Value Object | Description |
|--------------|-------------|
| [CompetitionFormat](competition-format.md) | ONLINE / OFFLINE / HYBRID |
| [CompetitionSchedule](competition-schedule.md) | Registration and team-formation date ranges |
| [CompetitionVenue](competition-venue.md) | Format and physical location |
| [ParticipantLimits](participant-limits.md) | Max participant count |
| [TeamSizeRange](team-size-range.md) | Min/max team size |
| [Milestone](milestone.md) | Custom timeline event |
| [MilestoneDescription](milestone-description.md) | Free-form milestone context (≤ 300 chars) |
| [Domain](domain.md) | IT domain area (Frontend, Backend, AI, …) |

## Participant

| Value Object | Description |
|--------------|-------------|
| [ParticipantType](participant-type.md) | Target audience category |
| [ParticipantSkill](participant-skill.md) | Skill with domain tag and level |
| [ParticipantContact](participant-contact.md) | External contact link |

## Application Form

| Value Object | Description |
|--------------|-------------|
| [Field](field.md) | A single form field definition |
| [FieldType](field-type.md) | STRING / INT / SELECT / MULTISELECT |
| [FieldChoice](field-choice.md) | A selectable option for SELECT/MULTISELECT fields |
