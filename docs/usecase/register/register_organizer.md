# RegisterOrganizer

## Purpose

Creates a new user and attaches organizer role to the user.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `organizer_name` | `str` | Organization name |
| `phone_number` | `str` | Contact phone number |
| `contact_email` | `str` | Contact email address |
| `invite_code` | `str` | Valid organizer invite code |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `organizer_id` | `OrganizerId` | Created organizer identifier |
| `user_id` | `UserId` | Created user identifier |

## Business Rules

1. Phone number and email combination must be unique
2. If user with given `auth_user_id` does not exist, create new user
3. If user with given `auth_user_id` exists, use existing user
4. Logo is set to `None` on registration
5. User can have only one organizer role
6. Invite code must exist, not be revoked, and not be used
7. When registration succeeds, invite is marked as used (`is_used = True`)

## Errors

| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `INVITE_NOT_FOUND` | 404 | Invite with given code does not exist |
| `INVITE_ALREADY_REVOKED` | 403 | Invite has been revoked by admin |
| `INVITE_ALREADY_USED` | 409 | Invite has already been used for another registration |
