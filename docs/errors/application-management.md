# Application Errors

[← Error Reference](index.md)

| Code | HTTP Status | Description | Metadata |
|------|-------------|-------------|----------|
| `APPLICATION_NOT_FOUND` | 404 | Application with the given ID does not exist | None |
| `APPLICATION_ALREADY_EXISTS` | 409 | Participant already has an application for this competition | None |
| `INVALID_APPLICATION_DATA` | 400 | Application data fails validation (bad track, form data mismatch, etc.) | None |
| `APPLICATION_ALREADY_RESOLVED` | 409 | Application is not in `PENDING` status and cannot be accepted, rejected, or withdrawn again | None |
| `APPLICATION_FORM_NOT_FOUND` | 404 | No ApplicationForm exists for the given competition | None |
| `APPLICATION_FORM_ALREADY_EXISTS` | 409 | An ApplicationForm already exists for the given competition; delete it before creating a new one | None |
| `INVALID_APPLICATION_FORM_DATA` | 400 | ApplicationForm definition is invalid (duplicate field names, bad choices config, etc.) | None |

## Related

- [Application entity](../entities/application.md)
- [ApplicationForm entity](../entities/application-form.md)
- [Submit Application](../usecase/submit_application/usecase.md)
- [View My Applications](../usecase/view_my_applications/usecase.md)
- [Submit Application](../usecase/submit_application/usecase.md)
- [View Submitted Applications](../usecase/view_submitted_applications/usecase.md)
- [Review Application](../usecase/review_application/usecase.md)
- [Manage Application Form](../usecase/manage_application_form/usecase.md)
