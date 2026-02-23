# OrganizerInvite

## Purpose

Represents an invitation to register as an organizer on the platform. Invites are issued by admin users and must be used during organizer registration to control access to organizer role creation.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `OrganizerInviteId` (UUID) | Invite identifier |
| `code` | `str` | Unique invite code used during registration |
| `display_name` | `str \| None` | Optional human-readable name for the invite |
| `created_by` | `UserId` (UUID) | Reference to admin user who created the invite |
| `is_revoked` | `bool` | Whether the invite has been revoked by admin |
| `is_used` | `bool` | Whether the invite has been used for registration |
| `created_at` | `datetime` | Timestamp when invite was created |

## Business Rules

1. Each invite code must be unique across all invites
2. Only admin users (`User.is_admin = True`) can create invites
3. Revoked invites cannot be used for registration
4. Used invites cannot be used again for registration
5. Revoked invites cannot be revoked again
6. Used invites cannot be revoked (prevents invalidating existing organizers)
7. When used during registration, `is_used` is set to `True`

## Relationships

```
OrganizerInvite 1 ──> 1 User (created_by)
```

- Each invite is created by exactly one admin user
