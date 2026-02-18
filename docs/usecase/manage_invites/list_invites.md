# ListInvites

## Purpose

Returns a paginated list of all organizer invites created by the current admin user.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `page` | `int` | Page number for pagination | Positive integer |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[InviteModel]` | List of invites |
| `total` | `int` | Total number of invites |
| `page` | `int` | Current page number |

### InviteModel

| Field | Type | Description |
|-------|------|-------------|
| `id` | `OrganizerInviteId` | Invite identifier |
| `code` | `str` | Unique invite code |
| `display_name` | `str \| None` | Optional display name |
| `created_by` | `UserId` | Admin user who created the invite |
| `is_revoked` | `bool` | Whether invite is revoked |
| `is_used` | `bool` | Whether invite is used |
| `created_at` | `datetime` | Creation timestamp |

## Business Rules

1. Only admin users (`User.is_admin = True`) can list invites
2. Only invites created by the current admin user are returned
3. Returns empty list if admin has created no invites
4. Results are ordered by `created_at` descending (newest first)
