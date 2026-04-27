# Value Objects

Value objects and validated value-object collections used within entities. Item value objects have no identity — two instances with equal fields are considered equal.

## Competition

| Value Object | Description |
|--------------|-------------|
| [CompetitionFormat](competition-format.md) | ONLINE / OFFLINE / HYBRID |
| [CompetitionSchedule](competition-schedule.md) | Registration and team-formation date ranges |
| [CompetitionVenue](competition-venue.md) | Format and physical location |
| [ParticipantLimits](participant-limits.md) | Max participant count |
| [TeamSizeRange](team-size-range.md) | Min/max team size |
| [Milestone](milestone.md) | Custom timeline event |
| [CompetitionMilestones](competition-milestones.md) | Competition milestone collection with unique timestamps |
| [Domain](domain.md) | IT domain area (Frontend, Backend, AI, …) |

## Participant

| Value Object | Description |
|--------------|-------------|
| [ParticipantType](participant-type.md) | Target audience category |
| [ParticipantSkill](participant-skill.md) | Skill name with proficiency level |
| [ParticipantSkills](participant-skills.md) | Participant skill collection with unique names |
| [ParticipantContact](participant-contact.md) | External contact value |
| [ParticipantContacts](participant-contacts.md) | Participant contact collection with unique titles and values |

## Application Form

| Value Object | Description |
|--------------|-------------|
| [Field](field.md) | A single form field definition |
| [FieldType](field-type.md) | STRING / INT / SELECT / MULTISELECT |
| [FieldChoice](field-choice.md) | A selectable option for SELECT/MULTISELECT fields |
| [ApplicationFormFields](application-form-fields.md) | Application form field collection with at least one unique-name field |
