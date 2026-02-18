# Use Case: Manage Invites

**Actor**: Admin User
**Module**: `application.manage_invites`

## Goal

Admin users manage organizer invitations to control who can register as an organizer on the platform.

## Interactors

- [IssueInvite](./issue_invite.md) — create new organizer invite
- [ListInvites](./list_invites.md) — list all invites created by admin
- [RevokeInvite](./revoke_invite.md) — revoke an existing invite
