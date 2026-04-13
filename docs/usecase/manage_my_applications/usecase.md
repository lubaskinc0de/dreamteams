# Use Case: Manage My Applications

**Actor**: Participant
**Module**: `application.manage_my_applications`

## Goal

A participant views and manages the applications they have submitted: browse their application history and withdraw applications they no longer wish to pursue (only while the application is still pending review).

## Interactors

- [ListMyApplications](./list_my_applications.md) — list all applications submitted by the current participant
- [WithdrawApplication](./withdraw_application.md) — withdraw a pending application (hard delete)
