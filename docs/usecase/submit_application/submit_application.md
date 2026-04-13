# SubmitApplication

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition to apply to | UUID format |
| `domains` | `list[Domain]` | Domains the participant wants to contribute to | At least one domain |
| `form_data` | `dict[str, Any] \| None` | Answers to the competition's ApplicationForm fields | Required when form exists; must be `None` otherwise |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `application_id` | `ApplicationId` | Identifier of the created application |

## Business Rules

1. User must have a Participant profile (`ACCESS_DENIED`)
2. Competition must exist (`COMPETITION_NOT_FOUND`)
3. `domains` must contain at least one entry and every domain must be a member of the competition's `domains` (`INVALID_APPLICATION_DATA`)
4. Participant must not already have an application for this competition (`APPLICATION_ALREADY_EXISTS`)
5. If the competition has an ApplicationForm, `form_data` must be provided and valid against that form (`INVALID_APPLICATION_DATA`)
6. If the competition has no ApplicationForm, `form_data` must be `None` (`INVALID_APPLICATION_DATA`)
7. If `competition.auto_accept = True`, the application is created with status `ACCEPTED`; otherwise `PENDING`
8. `id` and `created_at` are generated automatically
