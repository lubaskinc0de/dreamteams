# User & Organizer Errors

[← Error Reference](index.md)

## User Management

| Code | HTTP Status | Description | Metadata |
|------|-------------|-------------|----------|
| `ACCOUNT_BLOCKED` | 403 | Blocked user attempted to access an authenticated endpoint | `reason`, `blocked_at` |
| `USER_NOT_FOUND` | 404 | Attempting to access a user that does not exist | `user_id` |
| `AUTH_USER_ALREADY_EXISTS` | 409 | Attempting to create an auth user that already exists | `auth_user_id` |

## Organizer Management

| Code | HTTP Status | Description | Metadata |
|------|-------------|-------------|----------|
| `USER_ALREADY_ORGANIZER` | 409 | Attempting to create an organizer role for a user who is already an organizer | None |
| `ORGANIZER_ALREADY_EXISTS` | 409 | An organizer with the same phone number or email already exists | None |
| `ORGANIZER_USER_ID_MISMATCH` | 400 | Attempting to attach an organizer to user B with a user ID of user A | None |

## Related

- [User entity](../entities/user.md)
- [User Bans](../user-bans.md)
- [Organizer entity](../entities/organizer.md)
- [Register Organizer use case](../usecase/register_user/register_organizer.md)
