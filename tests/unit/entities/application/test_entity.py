from uuid import uuid4

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dreamteams.entities.application.entity import Application, ApplicationStatus
from dreamteams.entities.common.identifiers import CompetitionId
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.entities.errors.application import ParticipantLimitsExceededError
from dreamteams_common.clock import Clock
from tests.unit.composite import valid_competition
from tests.unit.conftest import NOW
from tests.unit.helpers.facade import Gateway


def _pending_application(competition_id: CompetitionId, track: CompetitionTrack) -> Application:
    return Application(
        id=uuid4(),
        participant_id=uuid4(),
        competition_id=competition_id,
        track=track,
        status=ApplicationStatus.PENDING,
        created_at=NOW,
    )


@settings(max_examples=30)
@given(st.data())
def test_pending_application_can_be_accepted_below_participant_limit(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Accepting a pending application below participant capacity changes it to ACCEPTED."""
    # Arrange
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock, is_archived=False, is_open=True))
    competition.participant_limits = ParticipantLimits(max=2)
    application = _pending_application(competition.id, next(iter(competition.tracks)))

    # Act
    application.accept(organizer, competition, accepted_count=1)

    # Assert
    assert application.status == ApplicationStatus.ACCEPTED


@settings(max_examples=30)
@given(st.data())
def test_full_competition_rejects_application_accept(
    gateway: Gateway,
    clock: Clock,
    data: st.DataObject,
) -> None:
    """Accepting a pending application at participant capacity raises ParticipantLimitsExceededError."""
    # Arrange
    organizer = gateway.organizer.create()
    competition = data.draw(valid_competition(organizer, clock, is_archived=False, is_open=True))
    competition.participant_limits = ParticipantLimits(max=1)
    application = _pending_application(competition.id, next(iter(competition.tracks)))

    # Act / Assert
    with pytest.raises(ParticipantLimitsExceededError):
        application.accept(organizer, competition, accepted_count=1)
    assert application.status == ApplicationStatus.PENDING
