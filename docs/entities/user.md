# User

## Purpose

Represents a user in the system. Acts as a container for user roles (organizer, participant).

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `UserId` (UUID) | User identifier |
| `is_admin` | `bool` | Whether user has admin privileges |
| `organizer` | [`Organizer`](organizer.md)` \| None` | Organizer role attached to user |
| `ban_status` | `BanStatus` | Account block state, optional reason, and block timestamp |

## Business Rules

1. User SHOULD have `Organizer` OR `Participant` role
2. When attaching organizer role, `<role>.user_id` must equal `user.id`
3. Admin users (`is_admin = True`) have elevated privileges for managing invites and system administration
4. Regular users have `is_admin = False` by default
5. Only admins can block or unblock user accounts
6. Fresh users are unblocked by default

## Relationships

```
User 1 ──> 0..1 Organizer
```

- One user can have zero or one organizer role

## Related

- [User Bans](../user-bans.md)
