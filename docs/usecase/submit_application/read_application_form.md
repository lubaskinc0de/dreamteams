# ReadApplicationForm

**Actor**: Participant — see [manage_application_form/read_application_form.md](../manage_application_form/read_application_form.md) for the organizer variant.

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
| `type` | `FieldType` | `STRING`, `INT`, `SELECT`, or `MULTISELECT` |
| `required` | `bool` | Whether the field is mandatory |
| `choices` | `list[FieldChoiceModel] \| None` | Options for `SELECT`/`MULTISELECT` fields; `None` for others |

### FieldChoiceModel

| Field | Type | Description |
|-------|------|-------------|
| `value` | `str` | Machine-readable option key |

## Business Rules

1. User must have a Participant profile (`ACCESS_DENIED`)
2. Competition must exist (`COMPETITION_NOT_FOUND`)
3. Form must exist for the competition (`APPLICATION_FORM_NOT_FOUND`)
