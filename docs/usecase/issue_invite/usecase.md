# Use Case: Issue Invite

**Actor**: Admin
**Module**: `application.issue_invite`

## Goal

Admin users issue organizer invitations, inspect individual invite codes, and revoke issued invites.

## Interactors

- [IssueInvite](./issue_invite.md) — create new organizer invite
- [ReadInvite](./read_invite.md) — retrieve a single invite by ID
- [RevokeInvite](./revoke_invite.md) — revoke an existing invite
