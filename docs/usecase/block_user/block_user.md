# BlockUser

## Purpose

Bans a user account. A banned user keeps all database records, but authenticated API access is denied until an admin unbans the account.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `target_user_id` | `UserId` | User account to ban | UUID format |
| `reason` | `str \| None` | Optional reason for the ban | May be `null` |

## Output

No response body.

## Business Rules

1. Only admin users (`User.is_admin = True`) can ban users
2. The authenticated admin user must exist
3. The target user must exist
4. The target user's `ban_status.is_blocked` is set to `true`
5. `ban_status.reason` stores the optional reason
6. `ban_status.blocked_at` stores the ban timestamp

## Errors

| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `USER_NOT_FOUND` | 404 | Authenticated admin or target user does not exist |
| `ACCESS_DENIED` | 403 | Authenticated user is not an admin |
