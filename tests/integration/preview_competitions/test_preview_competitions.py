from datetime import UTC, datetime, timedelta

from dreamteams.application.common.dto.milestone import MilestoneForm
from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_competitions import CompetitionModel
from dreamteams.application.manage_competitions.update import UpdateCompetitionForm
from dreamteams.application.preview_competition.list import PreviewCompetitionsList
from dreamteams.entities.competition.schedule import ScheduleData
from tests.integration.api_client import ApiClient
from tests.integration.manage_competitions.helpers import (
    competitions_list_to_preview_list,
    create_competitions_list,
    update_competition,
)


async def make_all_not_archived(api_client: ApiClient, competitions: list[CompetitionModel]) -> list[CompetitionModel]:
    """Make all passed competitions not archived and return updated competitions."""
    return [
        await update_competition(
            comp.id,
            UpdateCompetitionForm(
                title=comp.title,
                description=comp.description,
                schedule=ScheduleData(
                    registration_start=comp.schedule.registration_start,
                    registration_end=comp.schedule.registration_end,
                    team_formation_start=comp.schedule.team_formation_start,
                    team_formation_end=comp.schedule.team_formation_end,
                ),
                participant_limits=comp.participant_limits,
                participant_type=comp.participant_type,
                venue=comp.venue,
                team_size=comp.team_size,
                milestones=[MilestoneForm(title=m.title, timestamp=m.timestamp) for m in comp.milestones],
                is_archived=False,
                domains=comp.domains,
            ),
            api_client,
        )
        for comp in competitions
    ]


async def make_all_active(api_client: ApiClient, competitions: list[CompetitionModel]) -> list[CompetitionModel]:
    """Make all passed competitions active and return updated competitions."""
    return [
        await update_competition(
            comp.id,
            UpdateCompetitionForm(
                title=comp.title,
                description=comp.description,
                schedule=ScheduleData(
                    registration_start=datetime.now(tz=UTC) - timedelta(minutes=1),
                    registration_end=comp.schedule.registration_end,
                    team_formation_start=comp.schedule.team_formation_start,
                    team_formation_end=comp.schedule.team_formation_end,
                ),
                participant_limits=comp.participant_limits,
                participant_type=comp.participant_type,
                venue=comp.venue,
                team_size=comp.team_size,
                milestones=[MilestoneForm(title=m.title, timestamp=m.timestamp) for m in comp.milestones],
                is_archived=False,
                domains=comp.domains,
            ),
            api_client,
        )
        for comp in competitions
    ]





async def test_preview_competitions_lists_active_competitions(
    api_client: ApiClient,
    competitions: list[CompetitionModel],
) -> None:
    """Test listing competitions as unauthorized user shows only active competitions."""
    competitions = await make_all_active(api_client, competitions)
    expected_model = competitions_list_to_preview_list(
        create_competitions_list(
            competitions,
            sort_by=CompetitionSortBy.CREATED_AT,
            sort_order=SortOrder.DESC,
        ),
    )

    list_response = await api_client.list_preview_competitions()

    result = list_response.assert_status(200).ensure_content()
    assert result == expected_model


async def test_preview_competitions_does_not_shows_archived_competitions(
    api_client: ApiClient,
    competitions: list[CompetitionModel],  # noqa: ARG001
) -> None:
    """Test listing competitions as unauthorized user does not show archived competitions."""
    list_response = await api_client.list_preview_competitions()

    result = list_response.assert_status(200).ensure_content()
    assert result == PreviewCompetitionsList(items=[], total=0, page=1)  # all archived


async def test_preview_competitions_does_not_shows_competitions_which_not_begin(
    api_client: ApiClient,
    competitions: list[CompetitionModel],
) -> None:
    """Test listing competitions as unauthorized user does not show competitions with reg start in future."""
    await make_all_not_archived(api_client, competitions)

    list_response = await api_client.list_preview_competitions()

    result = list_response.assert_status(200).ensure_content()
    assert result == PreviewCompetitionsList(items=[], total=0, page=1)  # all archived




# async def test_preview_competitions_sorted_by_created_at_desc(
#     api_client: ApiClient,
#     competitions: list[CompetitionModel],
# ) -> None:
#     """Preview competitions must be sorted by created_at DESC."""
#     competitions = await make_all_active()
    
#     li
    
