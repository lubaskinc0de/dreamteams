# Use Case: Submit Application

**Actor**: Participant
**Module**: `application.submit_application`

## Goal

Participant browses competitions they are currently eligible to join, with rich
filters and popularity-first sorting, reads a competition's application form (if any),
submits an application to join a specific one, and withdraws their own pending application.

## Interactors

- [ExploreCompetitions](./list_competitions.md) — list competitions the participant can submit to
- [ReadCompetition](./read_competition.md) — read a single competition's details
- [ReadApplicationForm](./read_application_form.md) — read a competition's application form before submitting
- [SubmitApplication](./submit_application.md) — submit a new application to a competition
- [WithdrawApplication](./withdraw_application.md) — withdraw a pending application
