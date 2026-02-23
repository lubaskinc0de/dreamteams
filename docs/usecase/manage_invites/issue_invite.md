# IssueInvite

## Purpose

Creates a new organizer invitation with a unique code. Only admin users can issue invites.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `display_name` | `str \| None` | Optional human-readable name for the invite | Optional |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `invite_id` | `OrganizerInviteId` | Created invite identifier |

## Business Rules

1. Only admin users (`User.is_admin = True`) can issue invites
2. System generates a unique invite code automatically
3. If no `display_name` provided, it is set to `None`
4. `is_revoked` and `is_used` are set to `False` on creation
5. `created_by` is set to the current admin user's ID
6. `created_at` is set to current timestamp
