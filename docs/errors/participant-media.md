# Participant & Media Errors

[← Error Reference](index.md)

## Participant Management

| Code | HTTP Status | Description | Metadata |
|------|-------------|-------------|----------|
| `INVALID_PARTICIPANT_DATA` | 400 | Participant data fails validation | None |

## Media & File Upload

| Code | HTTP Status | Description | Metadata |
|------|-------------|-------------|----------|
| `INVALID_AVATAR_ERROR` | 400 | Uploaded file is not a valid avatar image | `reason` |

## Related

- [Participant entity](../entities/participant.md)
- [Register Participant](../usecase/register/register_participant.md)
