from datetime import UTC, datetime, timedelta

import pytest

from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionVenue
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams.entities.errors.competition import InvalidCompetitionDataError
from dreamteams.entities.user import User


def test_update_competition_with_valid_milestones(
    competition: Competition,
    organizer_user: User,
    schedule: CompetitionSchedule,
    participant_limits: ParticipantLimits,
    domains: list[Domain],
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
    milestones: list[Milestone],
) -> None:
    """Test updating competition with valid milestones."""
    competition.update(
        user=organizer_user,
        title="Updated Title",
        description="Updated description",
        schedule=schedule,
        participant_limits=participant_limits,
        domains=domains,
        participant_type=ParticipantType.STUDENT,
        venue=venue,
        team_size=team_size,
        milestones=milestones,
        is_archived=False,
    )

    assert competition.milestones == milestones


def test_update_competition_with_duplicate_milestone_timestamps_raises_error(
    competition: Competition,
    organizer_user: User,
    schedule: CompetitionSchedule,
    participant_limits: ParticipantLimits,
    domains: list[Domain],
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
) -> None:
    """Test that updating competition with duplicate milestone timestamps raises error."""
    now = datetime.now(tz=UTC)
    duplicate_timestamp = now + timedelta(days=15)
    duplicate_milestones = [
        Milestone(timestamp=duplicate_timestamp, title="Stage 1"),
        Milestone(timestamp=duplicate_timestamp, title="Stage 2"),
    ]

    with pytest.raises(InvalidCompetitionDataError, match="Milestone timestamps must be unique"):
        competition.update(
            user=organizer_user,
            title="Updated Title",
            description="Updated description",
            schedule=schedule,
            participant_limits=participant_limits,
            domains=domains,
            participant_type=ParticipantType.STUDENT,
            venue=venue,
            team_size=team_size,
            milestones=duplicate_milestones,
            is_archived=False,
        )


@pytest.mark.parametrize(
    ("description", "test_domains", "expected_error"),
    [
        ("", [Domain.AI], "Description must not be empty"),
        ("   ", [Domain.AI], "Description must not be empty"),
        ("Valid description", [], "Domains list must not be empty"),
    ],
)
def test_update_competition_with_invalid_data_raises_error(
    competition: Competition,
    organizer_user: User,
    schedule: CompetitionSchedule,
    participant_limits: ParticipantLimits,
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
    description: str,
    test_domains: list[Domain],
    expected_error: str,
) -> None:
    """Test that updating with invalid data raises appropriate errors."""
    with pytest.raises(InvalidCompetitionDataError, match=expected_error):
        competition.update(
            user=organizer_user,
            title="Updated Title",
            description=description,
            schedule=schedule,
            participant_limits=participant_limits,
            domains=test_domains,
            participant_type=ParticipantType.STUDENT,
            venue=venue,
            team_size=team_size,
            milestones=[],
            is_archived=False,
        )


def test_update_competition_by_non_organizer_raises_error(
    competition: Competition,
    user_without_organizer: User,
    schedule: CompetitionSchedule,
    participant_limits: ParticipantLimits,
    domains: list[Domain],
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
) -> None:
    """Test that updating competition by non-organizer raises error."""
    with pytest.raises(AccessDeniedError):
        competition.update(
            user=user_without_organizer,
            title="Updated Title",
            description="Updated description",
            schedule=schedule,
            participant_limits=participant_limits,
            domains=domains,
            participant_type=ParticipantType.STUDENT,
            venue=venue,
            team_size=team_size,
            milestones=[],
            is_archived=False,
        )


def test_update_competition_by_different_organizer_raises_error(
    competition: Competition,
    different_user: User,
    schedule: CompetitionSchedule,
    participant_limits: ParticipantLimits,
    domains: list[Domain],
    venue: CompetitionVenue,
    team_size: TeamSizeRange,
) -> None:
    """Test that updating competition by different organizer raises error."""
    with pytest.raises(AccessDeniedError):
        competition.update(
            user=different_user,
            title="Updated Title",
            description="Updated description",
            schedule=schedule,
            participant_limits=participant_limits,
            domains=domains,
            participant_type=ParticipantType.STUDENT,
            venue=venue,
            team_size=team_size,
            milestones=[],
            is_archived=False,
        )
