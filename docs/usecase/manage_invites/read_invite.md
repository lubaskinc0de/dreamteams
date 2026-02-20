# ReadInvite

## Purpose

Retrieves a single organizer invite by its ID. Only admin users can read invites.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `invite_id` | `OrganizerInviteId` | Invite identifier to read | UUID format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `id` | `OrganizerInviteId` | Invite identifier |
| `code` | `str` | Unique invite code |
| `display_name` | `str \| None` | Optional human-readable name |
| `created_by` | `UserId` | ID of the admin who created the invite |
| `is_revoked` | `bool` | Whether the invite has been revoked |
| `is_used` | `bool` | Whether the invite has been used |
| `created_at` | `datetime` | When the invite was created |

## Business Rules

1. Only admin users (`User.is_admin = True`) can read invites
2. Only the admin who created the invite can read it

## Errors

| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `INVITE_NOT_FOUND` | 404 | Invite with given ID does not exist |
| `ACCESS_DENIED` | 403 | Requester is not an admin, or is not the creator of the invite |
