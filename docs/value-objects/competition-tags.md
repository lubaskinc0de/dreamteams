# CompetitionTags

Validated collection of [`CompetitionTag`](../entities/competition-tag.md) entities attached to a competition.

## Rules

1. Tag IDs must be unique within a competition.
2. Tag values must be unique case-insensitively within a competition.
3. Competition create/update requests accept at most 30 tag IDs.
4. Tags come from the administrator-managed catalog; competitions reference existing tags.
