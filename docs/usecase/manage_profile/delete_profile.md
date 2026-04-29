# DeleteProfile

## Input

No explicit input. Uses `auth_user_id` from identity provider.

## Output

No output. Operation succeeds or raises error.

## Business Rules

1. User must exist (`USER_NOT_FOUND`)
2. The authenticated user's profile is deleted
3. Deletion is committed through the unit of work
