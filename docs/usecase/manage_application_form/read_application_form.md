# ReadApplicationForm

**Actor**: Organizer — see [submit_application/read_application_form.md](../submit_application/read_application_form.md) for the participant variant.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `competition_id` | `CompetitionId` | Competition identifier | UUID format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `id` | `ApplicationFormId` | Form identifier |
| `competition_id` | `CompetitionId` | Owning competition identifier |
| `created_at` | `datetime` | When the form was created |
| `fields` | `list[FieldModel]` | Field definitions |

### FieldModel

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Machine-readable field identifier |
| `label` | `str` | Human-readable field label |
| `type` | `FieldType` | `STRING`, `INT`, `SELECT`, or `MULTISELECT` |
| `required` | `bool` | Whether the field is mandatory |
| `choices` | `list[FieldChoiceModel] \| None` | Options for `SELECT`/`MULTISELECT` fields; `None` for others |

### FieldChoiceModel

| Field | Type | Description |
|-------|------|-------------|
| `value` | `str` | Machine-readable option key |
| `label` | `str` | Human-readable option display |

## Business Rules

1. Competition must exist (`COMPETITION_NOT_FOUND`)
2. Only the organizer who owns the competition can read its form (`ACCESS_DENIED`)
3. Form must exist for the competition (`APPLICATION_FORM_NOT_FOUND`)
