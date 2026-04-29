# Authentication & Authorization Errors

[← Error Reference](index.md)

| Code | HTTP Status | Description | Metadata |
|------|-------------|-------------|----------|
| `ACCESS_DENIED` | 403 | User attempts to access a resource they don't have permission for | None |
| `UNAUTHORIZED` | 401 | Request cannot be authenticated or authentication is invalid | `reason`, `header` |
| `MISSING_TRACE_ID` | 400 | Trace ID is required but cannot be extracted from request (when configured) | `header` |

## `UNAUTHORIZED` Reasons

The `UNAUTHORIZED` error includes a `reason` field in metadata:

| Reason | Description |
|--------|-------------|
| `MISSING_USER_ID` | User ID header is missing from request |
| `MISSING_USER_EMAIL` | User email header is missing from request |
| `INVALID_AUTH_USER_ID` | Auth user ID format is invalid |
| `MISSING_ACCESS_TOKEN` | Access token is missing |
| `CORRUPTED_ACCESS_TOKEN` | Access token is malformed or invalid |
| `EMAIL_IS_NOT_VERIFIED` | User email has not been verified |
