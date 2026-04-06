# ApplicationForm

## Purpose

Represents an optional set of extra input fields that an organizer can attach to a competition. When an ApplicationForm exists for a competition, participants must supply valid answers to all required fields when submitting an application.

## Attributes

| Attribute        | Type                        | Description                                                              |
| ---------------- | --------------------------- | ------------------------------------------------------------------------ |
| `id`             | `ApplicationFormId` (UUID)  | Unique identifier                                                        |
| `competition_id` | `CompetitionId` (UUID)      | The competition this form belongs to (one-to-one)                        |
| `created_at`     | `datetime`                  | When the form was created                                                |
| `fields`         | `frozenset[Field]`          | The set of fields participants must fill in; uniqueness enforced by `name` |

## Storage

`fields` is persisted as a JSON array in the database. Each element is a JSON object with the following shape:

```json
{
  "name": "tshirt_size",
  "label": "T-shirt size",
  "type": "SELECT",
  "required": true,
  "choices": [
    { "value": "S",  "label": "Small" },
    { "value": "M",  "label": "Medium" },
    { "value": "L",  "label": "Large" },
    { "value": "XL", "label": "Extra Large" }
  ]
}
```

For `STRING` / `INT` fields the `choices` key is omitted.

## Business Rules

1. Each competition can have **at most one** ApplicationForm (one-to-one relationship).
2. Field names within a form must be **unique** — duplicate `name` values are rejected.
3. A form must contain **at least one** field.
4. Only the organizer who owns the competition can create or delete the form.
5. Once a form is created it is **immutable** — to change it the organizer must delete the existing form and create a new one. (Immutability avoids inconsistency with already-submitted applications.)

## Relationships

```
ApplicationForm N ──> 1 Competition
ApplicationForm 1 ──> N Field
```

- Exactly one form per competition (optional on the competition side).
- Deleted together with the competition (cascade).

## Effect on Applications

When an ApplicationForm exists for a competition, the `Application.form_data` field is validated against the form at submission time:

- Every **required** field defined in the form must have a corresponding key in `form_data`.
- Optional fields may be omitted from `form_data`; if provided they are still validated.
- Values must match the field type:
  - `STRING` → any non-null string
  - `INT` → integer value
  - `SELECT` → a single `value` string that matches one of `choices[*].value`
  - `MULTISELECT` → a non-empty list of `value` strings, each matching one of `choices[*].value`
- Extra keys in `form_data` that are not declared in the form are rejected.
- If no ApplicationForm exists for the competition, `form_data` must be `None`.
