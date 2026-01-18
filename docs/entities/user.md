# User

## Purpose

Represents a user in the system. Acts as a container for user roles (organizer, participant).

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `UserId` (UUID) | User identifier |
| `organizer` | `Organizer \| None` | Organizer role attached to user |

## Business Rules

1. User can have at most one organizer role
2. When attaching organizer role, `organizer.user_id` must equal `user.id`

## Relationships

```
User 1 ──> 0..1 Organizer
```

- One user can have zero or one organizer role
