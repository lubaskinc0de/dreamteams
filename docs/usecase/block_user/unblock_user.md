# UnblockUser

## Purpose

Unbans a user account. After the account is unbanned, the user can make authenticated API requests again.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `target_user_id` | `UserId` | User account to unban | UUID format |

## Output

No response body.

## Business Rules

1. Only admin users (`User.is_admin = True`) can unban users
2. The authenticated admin user must exist
3. The target user must exist
4. The target user's `ban_status.is_blocked` is set to `false`
5. `ban_status.reason` and `ban_status.blocked_at` are cleared
6. The blocked-user cache entry is deleted after the database transaction commits

## Errors

| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `USER_NOT_FOUND` | 404 | Authenticated admin or target user does not exist |
| `ACCESS_DENIED` | 403 | Authenticated user is not an admin |
