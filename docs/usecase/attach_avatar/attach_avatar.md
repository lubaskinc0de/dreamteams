# AttachAvatar

## Input

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `file_data` | `BinaryIO` | Avatar file stream | Must be a valid image file at the HTTP boundary |
| `content_type` | `str` | Uploaded file MIME type | Must be an image MIME type at the HTTP boundary |

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. User must exist (`USER_NOT_FOUND`)
2. Existing avatar media is deleted before the new avatar is stored
3. User avatar key is updated and committed in the same unit of work
