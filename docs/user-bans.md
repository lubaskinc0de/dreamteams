# User Bans

Admin users can block and unblock user accounts through the admin user endpoints.

## Behavior

- Blocked users keep their database records and public data, but authenticated API access is rejected with `ACCOUNT_BLOCKED`.
- Block responses include the stored `reason` and `blocked_at` metadata when present.
- Unblocking clears the ban status and removes the blocked-user cache entry.
- Public competition previews hide competitions owned by blocked organizers.
- Organizer application lists hide applications submitted by blocked participants.

## Related Use Cases

- [Block User](usecase/block_user/block_user.md)
- [Unblock User](usecase/block_user/unblock_user.md)
- [View Users](usecase/view_users/usecase.md)
