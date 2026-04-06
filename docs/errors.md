# Backend Error Codes

## Purpose

This document describes all error codes that can be returned by the DreamTeams API. All application errors inherit from the `AppError` base class and follow a standardized structure with a `code`, `message`, and optional `meta` dictionary for additional context.

## Error Response Format

All API errors are returned in the following JSON format:

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable error description",
  "meta": {
    "additional": "context-specific metadata"
  }
}
```

## Error Codes

### Authentication & Authorization

| Code               | HTTP Status | Description                                                                 | Metadata                                      |
| ------------------ | ----------- | --------------------------------------------------------------------------- | --------------------------------------------- |
| `ACCESS_DENIED`    | 403         | User attempts to access a resource they don't have permission for           | None                                          |
| `UNAUTHORIZED`     | 401         | Request cannot be authenticated or authentication is invalid                | `reason`, `header`                            |
| `MISSING_TRACE_ID` | 400         | Trace ID is required but cannot be extracted from request (when configured) | `header`                                      |

#### `UNAUTHORIZED` Reasons

The `UNAUTHORIZED` error includes a `reason` field in metadata with one of the following values:

- `MISSING_USER_ID` - User ID header is missing from request
- `MISSING_USER_EMAIL` - User email header is missing from request
- `INVALID_AUTH_USER_ID` - Auth user ID format is invalid
- `MISSING_ACCESS_TOKEN` - Access token is missing
- `CORRUPTED_ACCESS_TOKEN` - Access token is malformed or invalid
- `EMAIL_IS_NOT_VERIFIED` - User email has not been verified

### User Management

| Code                       | HTTP Status | Description                                                  | Metadata      |
| -------------------------- | ----------- | ------------------------------------------------------------ | ------------- |
| `USER_NOT_FOUND`           | 404         | Attempting to access a user that does not exist in the system | `user_id`     |
| `AUTH_USER_ALREADY_EXISTS` | 409         | Attempting to create an auth user that already exists        | `auth_user_id` |

### Organizer Management

| Code                           | HTTP Status | Description                                                                      | Metadata |
| ------------------------------ | ----------- | -------------------------------------------------------------------------------- | -------- |
| `USER_ALREADY_ORGANIZER`       | 409         | Attempting to create an organizer role for a user who is already an organizer   | None     |
| `ORGANIZER_ALREADY_EXISTS`     | 409         | An organizer with the same phone number or email already exists                 | None     |
| `ORGANIZER_USER_ID_MISMATCH`   | 400         | Attempting to attach an organizer to user B with a user ID of user A            | None     |

### Invite Management

| Code                           | HTTP Status | Description                                                                      | Metadata |
| ------------------------------ | ----------- | -------------------------------------------------------------------------------- | -------- |
| `INVITE_NOT_FOUND`             | 404         | Invite with given ID or code does not exist                                     | None     |
| `INVITE_ALREADY_REVOKED`       | 403/409     | Invite has been revoked and cannot be used (403) or revoked again (409)         | None     |
| `INVITE_ALREADY_USED`          | 409         | Invite has already been used for registration                                    | None     |

### Competition Management

| Code                          | HTTP Status | Description                          | Metadata |
| ----------------------------- | ----------- | ------------------------------------ | -------- |
| `COMPETITION_NOT_FOUND`       | 404         | Competition does not exist           | None     |
| `INVALID_COMPETITION_DATA`    | 400         | Competition data fails validation    | None     |

### Application Management

| Code                              | HTTP Status | Description                                                                              | Metadata |
| --------------------------------- | ----------- | ---------------------------------------------------------------------------------------- | -------- |
| `INVALID_APPLICATION_DATA`        | 400         | Application data fails validation (bad domains, form data mismatch, etc.)               | None     |
| `APPLICATION_ALREADY_RESOLVED`    | 409         | Application is not in PENDING status and cannot be accepted or rejected again            | None     |
| `APPLICATION_FORM_NOT_FOUND`      | 404         | No ApplicationForm exists for the given competition                                      | None     |
| `INVALID_APPLICATION_FORM_DATA`   | 400         | ApplicationForm definition is invalid (duplicate field names, bad choices config, etc.) | None     |

### Participant Management

| Code                          | HTTP Status | Description                          | Metadata |
| ----------------------------- | ----------- | ------------------------------------ | -------- |
| `INVALID_PARTICIPANT_DATA`    | 400         | Participant data fails validation    | None     |

### Media & File Upload

| Code                    | HTTP Status | Description                                      | Metadata |
| ----------------------- | ----------- | ------------------------------------------------ | -------- |
| `INVALID_AVATAR_ERROR`  | 400         | Uploaded file is not a valid avatar image        | `reason` |

### Generic Errors

| Code                      | HTTP Status | Description                                                  | Metadata  |
| ------------------------- | ----------- | ------------------------------------------------------------ | --------- |
| `VALIDATION_ERROR`        | 422         | Request validation failed (invalid request body or parameters) | `details` |
| `INTERNAL_SERVER_ERROR`   | 500         | Unexpected exception occurred on the server                   | None      |
