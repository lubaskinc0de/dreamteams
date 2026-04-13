# CreateApplicationForm

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition to attach the form to | UUID format |
| `fields` | `list[FieldForm]` | Fields participants must fill in | At least one field |

### FieldForm

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `name` | `str` | Machine-readable field identifier | Non-empty; unique within the form |
| `label` | `str` | Human-readable field label | Non-empty |
| `type` | `FieldType` | Field data type | `STRING`, `INT`, `SELECT`, or `MULTISELECT` |
| `required` | `bool` | Whether the field is mandatory | Default `True` |
| `choices` | `list[FieldChoiceForm] \| None` | Selectable options | Required for `SELECT`/`MULTISELECT`; must be `None` for `STRING`/`INT` |

### FieldChoiceForm

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `value` | `str` | Machine-readable option key | Non-empty; unique within the field |
| `label` | `str` | Human-readable option display | Non-empty |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `application_form_id` | `ApplicationFormId` | Identifier of the created form |

## Business Rules

1. Only the organizer who created the competition can attach a form to it (`ACCESS_DENIED`)
2. Competition must exist (`COMPETITION_NOT_FOUND`)
3. Competition must not already have an application form — delete the existing one before creating a new one (`APPLICATION_FORM_ALREADY_EXISTS`)
4. At least one field is required (`INVALID_APPLICATION_FORM_DATA`)
5. Field `name` values must be unique within the form (`INVALID_APPLICATION_FORM_DATA`)
6. `SELECT` and `MULTISELECT` fields must have at least one choice; `STRING` and `INT` fields must have no choices (`INVALID_APPLICATION_FORM_DATA`)
7. Choice `value` strings must be unique within a field (`INVALID_APPLICATION_FORM_DATA`)
8. `id` and `created_at` are generated automatically
