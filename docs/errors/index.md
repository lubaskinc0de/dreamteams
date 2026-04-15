# Error Reference

All DreamTeams API errors inherit from `AppError` and return a standardized JSON body.

## Error Response Format

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable error description",
  "meta": {
    "additional": "context-specific metadata"
  }
}
```

The `meta` field is `{}` when no extra context is available.

## Error Categories

| Category | Codes |
|----------|-------|
| [Authentication & Authorization](auth.md) | `ACCESS_DENIED`, `UNAUTHORIZED`, `MISSING_TRACE_ID` |
| [User & Organizer](user-management.md) | `USER_NOT_FOUND`, `AUTH_USER_ALREADY_EXISTS`, `USER_ALREADY_ORGANIZER`, `ORGANIZER_ALREADY_EXISTS`, `ORGANIZER_USER_ID_MISMATCH` |
| [Invites](invite-management.md) | `INVITE_NOT_FOUND`, `INVITE_ALREADY_REVOKED`, `INVITE_ALREADY_USED` |
| [Competitions](competition-management.md) | `COMPETITION_NOT_FOUND`, `INVALID_COMPETITION_DATA` |
| [Applications](application-management.md) | `APPLICATION_NOT_FOUND`, `APPLICATION_ALREADY_EXISTS`, `INVALID_APPLICATION_DATA`, `APPLICATION_ALREADY_RESOLVED`, `APPLICATION_FORM_NOT_FOUND`, `APPLICATION_FORM_ALREADY_EXISTS`, `INVALID_APPLICATION_FORM_DATA` |
| [Participants & Media](participant-media.md) | `INVALID_PARTICIPANT_DATA`, `INVALID_AVATAR_ERROR` |
| [Generic](generic.md) | `VALIDATION_ERROR`, `INTERNAL_SERVER_ERROR` |
