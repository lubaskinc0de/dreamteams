# Use Case: Manage Application Form

**Actor**: Organizer
**Module**: `application.manage_application_form`

## Goal

Organizer manages the optional application form attached to their competition: create a form with custom fields, view the current form definition, and delete it (deletion is required before creating a replacement, since the form is immutable once created).

## Interactors

- [CreateApplicationForm](./create_application_form.md) — attach a new form to a competition
- [ReadApplicationForm](./read_application_form.md) — read the current form definition
- [DeleteApplicationForm](./delete_application_form.md) — remove the form from a competition
