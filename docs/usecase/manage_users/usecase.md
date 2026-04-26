# Use Case: Manage Users

**Actor**: Admin User
**Module**: `application.manage_users`

## Goal

Admin users manage user accounts across the platform. They can list users, inspect a user's complete profile data, and control account access through ban and unban operations.

## Interactors

- [BlockUser](./block_user.md) - ban a user account
- [UnblockUser](./unblock_user.md) - unban a user account
- [ListUsers](./list_users.md) - list users for the admin interface
- [ReadUserByAdmin](./read_user_by_admin.md) - retrieve full user details for admin review
