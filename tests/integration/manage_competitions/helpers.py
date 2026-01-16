from collections.abc import Callable
from datetime import datetime

from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_competitions.list import PAGE_SIZE, CompetitionsList
from dreamteams.application.manage_competitions.read import CompetitionModel
from dreamteams.application.manage_competitions.update import UpdateCompetitionForm
from dreamteams.application.publish_competition.create import CompetitionForm
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.schedule import schedule_factory
from tests.integration.api_client import ApiClient
from tests.integration.conftest import USER_ID


def create_competitions_list(
    competitions: list[CompetitionModel],
    sort_by: CompetitionSortBy | None,
    sort_order: SortOrder | None,
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> CompetitionsList:
    """Create ``CompetitionsList`` from ``list[CompetitionModel]`` with sorting and pagination applied."""
    sort_key_mapping: dict[CompetitionSortBy, Callable[[CompetitionModel], tuple[datetime | str, CompetitionId]]] = {
        CompetitionSortBy.CREATED_AT: lambda c: (c.created_at, c.id),
        CompetitionSortBy.TITLE: lambda c: (c.title, c.id),
        CompetitionSortBy.REGISTRATION_START: lambda c: (c.schedule.registration_start, c.id),
    }

    sorted_items = (
        sorted(
            competitions,
            key=sort_key_mapping[sort_by],
            reverse=(sort_order == SortOrder.DESC),
        )
        if sort_by is not None and sort_order is not None
        else competitions
    )

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = sorted_items[start_idx:end_idx]

    return CompetitionsList(
        items=paginated_items,
        total=len(competitions),
        page=page,
    )


async def update_competition(
    competition_id: CompetitionId,
    data: UpdateCompetitionForm,
    api_client: ApiClient,
    user_id: str = USER_ID,
) -> CompetitionModel:
    """Update competition and read updated model."""
    with api_client.authenticate(auth_user_id=user_id):
        update_response = await api_client.update_competition(competition_id, data.model_dump(mode="json"))
        update_response.assert_status(200)

        return (await api_client.read_competition(competition_id)).assert_status(200).ensure_content()


def competition_form_to_model(
    competition_id: CompetitionId,
    organizer_id: OrganizerId,
    created_at: datetime,
    updated_at: datetime,
    form: CompetitionForm,
) -> CompetitionModel:
    """Transform competition form and additional data to CompetitionModel."""
    return CompetitionModel(
        id=competition_id,
        organizer_id=organizer_id,
        title=form.title,
        banner=None,
        description=form.description,
        schedule=schedule_factory(form.schedule),
        participant_limits=form.participant_limits,
        domains=form.domains,
        participant_type=form.participant_type,
        venue=form.venue,
        team_size=form.team_size,
        milestones=[
            Milestone(timestamp=milestone.timestamp, title=milestone.title)
            for milestone in sorted(form.milestones, key=lambda item: item.timestamp)
        ],
        is_archived=True,
        created_at=created_at,
        updated_at=updated_at,
    )


def competition_update_form_to_model(
    competition_id: CompetitionId,
    organizer_id: OrganizerId,
    created_at: datetime,
    updated_at: datetime,
    form: UpdateCompetitionForm,
) -> CompetitionModel:
    """Transform competition form and additional data to CompetitionModel."""
    return CompetitionModel(
        id=competition_id,
        organizer_id=organizer_id,
        title=form.title,
        banner=None,
        description=form.description,
        schedule=schedule_factory(form.schedule),
        participant_limits=form.participant_limits,
        domains=form.domains,
        participant_type=form.participant_type,
        venue=form.venue,
        team_size=form.team_size,
        milestones=[
            Milestone(timestamp=milestone.timestamp, title=milestone.title)
            for milestone in sorted(form.milestones, key=lambda item: item.timestamp)
        ]
        if form.milestones
        else [],
        is_archived=form.is_archived,
        created_at=created_at,
        updated_at=updated_at,
    )
