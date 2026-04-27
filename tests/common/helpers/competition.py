from datetime import UTC, datetime, timedelta
from typing import Any


def schedule_from_deltas(
    *,
    registration_start: timedelta,
    registration_end: timedelta,
    team_formation_start: timedelta | None = None,
    team_formation_end: timedelta | None = None,
) -> dict[str, Any]:
    """Convert timedelta values to ISO datetime strings for CompetitionSchedule."""
    now = datetime.now(tz=UTC)
    result = {
        "registration_start": (now + registration_start).isoformat(),
        "registration_end": (now + registration_end).isoformat(),
    }
    if team_formation_start is not None:
        result["team_formation_start"] = (now + team_formation_start).isoformat()
    if team_formation_end is not None:
        result["team_formation_end"] = (now + team_formation_end).isoformat()
    return result


def milestones_from_deltas(milestones: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert milestones with timedelta timestamps to ISO datetime strings."""
    now = datetime.now(tz=UTC)
    return [
        {"timestamp": (now + milestone["timestamp"]).isoformat(), "title": milestone["title"]}
        for milestone in milestones
    ]


INVALID_COMPETITION_DATA_CASES: list[tuple[dict[str, Any], str]] = [
    # Title validation
    ({"title": "a" * 300}, "VALIDATION_ERROR"),  # Title exceeds max length (200 characters)
    # Description validation
    ({"description": ""}, "VALIDATION_ERROR"),  # Description cannot be empty
    # Domains validation
    ({"domains": []}, "INVALID_COMPETITION_DATA"),  # Domains list cannot be empty
    # Participant limits: max is zero
    ({"participant_limits": {"max": 0}}, "INVALID_COMPETITION_DATA"),
    # Participant limits: max is negative
    ({"participant_limits": {"max": -10}}, "INVALID_COMPETITION_DATA"),
    # Team size: min exceeds max
    ({"team_size": {"max": 3, "min": 10}}, "INVALID_COMPETITION_DATA"),
    # Team size: max is zero
    ({"team_size": {"max": 0, "min": 1}}, "INVALID_COMPETITION_DATA"),
    # Team size: min is zero (must be at least 1)
    ({"team_size": {"max": 5, "min": 0}}, "INVALID_COMPETITION_DATA"),
    # Schedule validation: registration start equals registration end
    (
        {
            "schedule": {
                "registration_start": timedelta(days=5),
                "registration_end": timedelta(days=5),
            },
        },
        "INVALID_COMPETITION_DATA",
    ),
    # Venue: offline format requires location
    ({"venue": {"format": "offline", "location": ""}}, "INVALID_COMPETITION_DATA"),
    ({"venue": {"format": "offline", "location": "   "}}, "INVALID_COMPETITION_DATA"),
    # Venue: hybrid format requires location
    ({"venue": {"format": "hybrid", "location": ""}}, "INVALID_COMPETITION_DATA"),
    ({"venue": {"format": "hybrid", "location": "   "}}, "INVALID_COMPETITION_DATA"),
    # Team formation: only start specified (both must be specified together)
    (
        {
            "schedule": {
                "registration_start": timedelta(days=1),
                "registration_end": timedelta(days=10),
                "team_formation_start": timedelta(days=11),
            },
        },
        "INVALID_COMPETITION_DATA",
    ),
    # Team formation: only end specified (both must be specified together)
    (
        {
            "schedule": {
                "registration_start": timedelta(days=1),
                "registration_end": timedelta(days=10),
                "team_formation_end": timedelta(days=12),
            },
        },
        "INVALID_COMPETITION_DATA",
    ),
    # Team formation: starts before registration end
    (
        {
            "schedule": {
                "registration_start": timedelta(days=1),
                "registration_end": timedelta(days=10),
                "team_formation_start": timedelta(days=9),
                "team_formation_end": timedelta(days=12),
            },
        },
        "INVALID_COMPETITION_DATA",
    ),
    # Pairing invariant: schedule has no team_formation but team_size is set (from factory base)
    (
        {
            "schedule": {
                "registration_start": timedelta(days=1),
                "registration_end": timedelta(days=10),
            },
        },
        "INVALID_COMPETITION_DATA",
    ),
    # Pairing invariant: team_size is None but schedule.team_formation_* are set (from factory base)
    (
        {"team_size": None},
        "INVALID_COMPETITION_DATA",
    ),
    # Milestones: duplicate timestamps
    (
        {
            "milestones": [
                {"timestamp": timedelta(days=15), "title": "Stage 1"},
                {"timestamp": timedelta(days=15), "title": "Stage 2"},
            ],
        },
        "INVALID_COMPETITION_DATA",
    ),
    # Milestones: empty title
    (
        {
            "milestones": [
                {"timestamp": timedelta(days=20), "title": ""},
            ],
        },
        "VALIDATION_ERROR",
    ),
    # Milestones: too long title
    (
        {
            "milestones": [
                {"timestamp": timedelta(days=15), "title": "a" * 300},
            ],
        },
        "VALIDATION_ERROR",
    ),
    # Milestones: timestamp in past  # noqa: ERA001
    (
        {
            "milestones": [
                {"timestamp": timedelta(days=-1), "title": "Stage 1"},
            ],
        },
        "INVALID_COMPETITION_DATA",
    ),
]
