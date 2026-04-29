# DetachAvatar

## Input

No explicit input. Uses `auth_user_id` from identity provider.

## Output

No output. Operation succeeds or is a no-op when the user has no avatar.

## Business Rules

1. User must exist (`USER_NOT_FOUND`)
2. Existing avatar media is deleted from storage
3. User avatar key is cleared and committed in the same unit of work
