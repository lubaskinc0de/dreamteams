from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import pytest

from dreamteams.application.common.competition_input_limits import (
    MAX_COMPETITION_DESCRIPTION_LENGTH,
    MAX_COMPETITION_MILESTONES,
    MAX_COMPETITION_TRACKS,
    MAX_LOCATION_LENGTH,
    MAX_PARTICIPANTS,
    MAX_TEAM_SIZE,
)
from dreamteams.application.common.dto.competition_track import CompetitionTrackForm
from dreamteams.application.common.dto.milestone import MilestoneForm
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionFormat, CompetitionVenue
from dreamteams_common.clock import Clock
from tests.common.factory.competition import CompetitionFormFactory
from tests.common.helpers.competition import (
    INVALID_COMPETITION_DATA_CASES,
    milestones_from_deltas,
    schedule_from_deltas,
)
from tests.integration.api_client import ApiClient
from tests.integration.competition_helpers import competition_form_to_model
from tests.integration.helpers.facade import Gateway


async def test_create_competition_as_organizer_succeeds(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Test creating competition as organizer."""
    organizer = await gateway.organizer.create_with_admin(gateway.admin)

    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.create_competition(competition_form_factory.build().model_dump(mode="json"))

    response.assert_status(200).ensure_content()


async def test_create_competition_without_team_size_or_team_formation_succeeds(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Test creating competition without team_size and team_formation (both omitted together)."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)
    now = datetime.now(tz=UTC)
    schedule = ScheduleData(
        registration_start=now + timedelta(days=1),
        registration_end=now + timedelta(days=10),
        team_formation_start=None,
        team_formation_end=None,
    )
    form = competition_form_factory.build(team_size=None, schedule=schedule)

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.create_competition(form.model_dump(mode="json"))

    # Assert
    response.assert_status(200).ensure_content()


async def test_create_competition_persists_tags(
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
    clock: Clock,
) -> None:
    """Creating a competition with tag_ids returns the attached tag entities on read."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    backend, python = await gateway.tags.create_many_unique(
        owner.admin.auth_id,
        ["BackendCreateTag", "PythonCreateTag"],
    )

    form = competition_form_factory.build(tag_ids=[python.id, backend.id])

    # Act
    model = await gateway.competition.create_from_form(owner.organizer.auth_id, form)

    # Assert
    assert model == competition_form_to_model(
        competition_id=model.id,
        organizer_id=owner.organizer.created.organizer_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        form=form,
        clock=clock,
        tags=[backend, python],
    )


async def test_create_competition_rejects_more_than_thirty_tag_ids(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Creating a competition with more than 30 tag_ids is rejected by request validation."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    data = competition_form_factory.build().model_dump(mode="json")
    data["tag_ids"] = [str(uuid4()) for _ in range(31)]

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_competition(data)

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_create_competition_rejects_too_long_description(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Creating a competition with an oversized description is rejected by request validation."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    data = competition_form_factory.build().model_copy(
        update={"description": "a" * (MAX_COMPETITION_DESCRIPTION_LENGTH + 1)},
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_competition(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_create_competition_rejects_too_many_tracks(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Creating a competition with too many tracks is rejected by request validation."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    data = competition_form_factory.build().model_copy(
        update={
            "tracks": [CompetitionTrackForm(name=f"track-{i}") for i in range(MAX_COMPETITION_TRACKS + 1)],
        },
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_competition(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_create_competition_rejects_too_many_milestones(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Creating a competition with too many milestones is rejected by request validation."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    now = datetime.now(tz=UTC)
    data = competition_form_factory.build().model_copy(
        update={
            "milestones": [
                MilestoneForm(timestamp=now + timedelta(days=i + 1), title=f"Stage {i}", description=None)
                for i in range(MAX_COMPETITION_MILESTONES + 1)
            ],
        },
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_competition(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_create_competition_rejects_too_large_participant_limit(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Creating a competition with an impractically large participant limit is rejected."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    base = competition_form_factory.build()
    data = base.model_copy(
        update={
            "participant_limits": ParticipantLimits(max=MAX_PARTICIPANTS + 1),
        },
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_competition(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_create_competition_rejects_too_large_team_size(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Creating a competition with an impractically large team size is rejected."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    base = competition_form_factory.build()
    data = base.model_copy(
        update={
            "team_size": TeamSizeRange(min=1, max=MAX_TEAM_SIZE + 1),
        },
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_competition(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_create_competition_rejects_too_long_location(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Creating a competition with an impractically long location is rejected."""
    # Arrange
    owner = await gateway.organizer.create_with_admin(gateway.admin)
    base = competition_form_factory.build()
    data = base.model_copy(
        update={
            "venue": CompetitionVenue(
                format=CompetitionFormat.OFFLINE,
                location="a" * (MAX_LOCATION_LENGTH + 1),
            ),
        },
    )

    # Act
    with api_client.authenticate(auth_user_id=owner.organizer.auth_id):
        response = await api_client.create_competition(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


async def test_create_competition_fails_if_description_is_empty(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
) -> None:
    """Test creating competition with empty description is rejected with 422."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)
    data = competition_form_factory.build().model_copy(update={"description": ""})

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.create_competition(data.model_dump(mode="json"))

    # Assert
    response.assert_error(422, "VALIDATION_ERROR")


@pytest.mark.parametrize(("update_data", "expected_error"), INVALID_COMPETITION_DATA_CASES)
async def test_create_competition_with_invalid_data(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
    gateway: Gateway,
    update_data: dict[str, Any],
    expected_error: str,
) -> None:
    """Test creating competition with invalid data."""
    # Arrange
    organizer = await gateway.organizer.create_with_admin(gateway.admin)
    base_data = competition_form_factory.build().model_dump(mode="json")

    update_data = update_data.copy()
    if "schedule" in update_data:
        update_data["schedule"] = schedule_from_deltas(**update_data["schedule"])
    if "milestones" in update_data:
        update_data["milestones"] = milestones_from_deltas(update_data["milestones"])
    base_data.update(update_data)

    # Act
    with api_client.authenticate(auth_user_id=organizer.organizer.auth_id):
        response = await api_client.create_competition(base_data)

    # Assert
    response.assert_error(422, expected_error)


async def test_create_competition_fails_if_unauthorized(
    api_client: ApiClient,
    competition_form_factory: CompetitionFormFactory,
) -> None:
    """Test creating competition fails when user is unauthorized."""
    data = competition_form_factory.build().model_dump(mode="json")

    response = await api_client.create_competition(data)

    response.assert_error(401, "UNAUTHORIZED")
