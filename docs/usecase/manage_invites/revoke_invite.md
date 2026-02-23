# RevokeInvite

## Purpose

Revokes an existing organizer invite, preventing it from being used for registration. Only admin users can revoke invites.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `invite_id` | `OrganizerInviteId` | Invite identifier to revoke | UUID format |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. Only admin users (`User.is_admin = True`) can revoke invites
2. Only the admin who created the invite can revoke it
3. Cannot revoke an invite that is already revoked (raises `INVITE_ALREADY_REVOKED`)
4. Cannot revoke an invite that has been used (raises `INVITE_ALREADY_USED`)
5. Sets `is_revoked` to `True` on successful revocation

## Errors

| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `INVITE_NOT_FOUND` | 404 | Invite with given ID does not exist |
| `INVITE_ALREADY_REVOKED` | 409 | Invite is already revoked |
| `INVITE_ALREADY_USED` | 409 | Invite has already been used for registration |
| `ACCESS_DENIED` | 403 | Admin user is not the creator of the invite |
