# ReadUserByAdmin

## Purpose

Retrieves full user, organizer, and participant information for admin review.

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `user_id` | `UserId` | User account to read | UUID format |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `user` | `AdminUserModel` | Full user information |
| `organizer` | `AdminOrganizerModel \| None` | Full organizer information if the user has an organizer role |
| `participant` | `AdminParticipantModel \| None` | Full participant information if the user has a participant role |

### AdminUserModel

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UserId` | User identifier |
| `avatar_url` | `str \| None` | Public avatar URL if the user has an avatar |
| `is_admin` | `bool` | Whether the user has admin privileges |
| `ban_status` | `BanStatusModel` | Account ban state |

### BanStatusModel

| Field | Type | Description |
|-------|------|-------------|
| `is_blocked` | `bool` | Whether the account is banned |
| `reason` | `str \| None` | Ban reason if present |
| `blocked_at` | `datetime \| None` | Ban timestamp if present |

### AdminOrganizerModel

| Field | Type | Description |
|-------|------|-------------|
| `id` | `OrganizerId` | Organizer identifier |
| `user_id` | `UserId` | Associated user identifier |
| `organizer_name` | `str` | Organization name |
| `phone_number` | `str` | Contact phone |
| `contact_email` | `str` | Contact email |

### AdminParticipantModel

| Field | Type | Description |
|-------|------|-------------|
| `id` | `ParticipantId` | Participant identifier |
| `user_id` | `UserId` | Associated user identifier |
| `full_name` | `str` | Full participant name |
| `participant_type` | `ParticipantType` | Participant type |
| `age` | `int` | Participant age |
| `bio` | `str \| None` | Short biography |
| `skills` | `list[ParticipantSkill]` | Participant skills |
| `experience_level` | `ExperienceLevel \| None` | Experience level |
| `contacts` | `list[ParticipantContact]` | Contact values |
| `created_at` | `datetime` | Profile creation timestamp |
| `updated_at` | `datetime` | Last profile update timestamp |

## Business Rules

1. Only admin users (`User.is_admin = True`) can read user details through this interactor
2. The authenticated admin user must exist
3. The target user must exist
4. Organizer and participant sections are returned as `null` when the target user does not have that role
5. Blocked users can still be read by admins

## Errors

| Error Code | HTTP Status | Condition |
|-----------|-------------|-----------|
| `USER_NOT_FOUND` | 404 | Authenticated admin or target user does not exist |
| `ACCESS_DENIED` | 403 | Authenticated user is not an admin |
