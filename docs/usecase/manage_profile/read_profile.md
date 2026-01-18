# ReadProfile

## Input

No explicit input. Uses `auth_user_id` from identity provider.

## Output

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | `UserId` | User identifier |
| `organizer` | `OrganizerModel \| None` | Organizer information if role assigned |

### OrganizerModel

| Field | Type | Description |
|-------|------|-------------|
| `id` | `OrganizerId` | Organizer identifier |
| `user_id` | `UserId` | User identifier |
| `organizer_name` | `str` | Organization name |
| `phone_number` | `str` | Contact phone |
| `contact_email` | `str` | Contact email |
| `logo` | `Logo \| None` | Organization logo |

## Business Rules

1. Only authenticated users can view profile
2. User can view only their own profile
3. User must have assigned role
