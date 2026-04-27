# CompetitionTracks

Validated collection of [`CompetitionTrack`](competition-track.md) values owned by a competition.

## Rules

1. Track names must be unique case-insensitively within a competition.
2. Competition create/update requires at least one track at the application boundary.
3. Tracks are stored in a separate database table and are deleted with their competition.
