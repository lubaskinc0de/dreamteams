import random
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models import competition_table
from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_competitions import CompetitionModel
from dreamteams.application.manage_competitions.list import PAGE_SIZE, CompetitionsList
from dreamteams.application.manage_competitions.update import UpdateCompetitionForm
from dreamteams.application.preview_competition.list import (
    PreviewCompetitionModel,
    PreviewCompetitionsList,
    PreviewOrganizerModel,
)
from dreamteams.application.publish_competition.create import CompetitionForm
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import schedule_factory
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm
from tests.common.factory.competition import UpdateCompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.constants import USER_ID


async def _update_competition_directly(
    session: AsyncSession,
    competition_id: CompetitionId,
    **values: Any,
) -> None:
    """Update competition fields directly in the database, bypassing entity creation rules."""
    values["updated_at"] = datetime.now(tz=UTC)
    await session.execute(
        update(competition_table).where(competition_table.c.id == competition_id).values(**values),
    )
    await session.commit()


async def read_competition(api_client: ApiClient, competition_id: CompetitionId) -> CompetitionModel:
    """Read a competition via API."""
    with api_client.authenticate(auth_user_id=USER_ID):
        return (await api_client.read_competition(competition_id)).assert_status(200).ensure_content()


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


async def make_all_active(
    session: AsyncSession,
    api_client: ApiClient,
    competitions: list[CompetitionModel],
) -> list[CompetitionModel]:
    """Make all competitions active (reg started, reg not ended, not archived)."""
    now = datetime.now(tz=UTC)
    result = []
    for comp in competitions:
        reg_end = comp.schedule.registration_end
        if reg_end <= now:
            reg_end = now + timedelta(days=7)

        tf_start = comp.schedule.team_formation_start
        tf_end = comp.schedule.team_formation_end
        if tf_start is not None and tf_start <= reg_end:
            tf_start = reg_end + timedelta(days=1)
            tf_end = tf_start + timedelta(days=3) if tf_end is not None else None

        await _update_competition_directly(
            session,
            comp.id,
            registration_start=now - timedelta(minutes=1),
            registration_end=reg_end,
            is_archived=False,
            team_formation_start=tf_start,
            team_formation_end=tf_end,
        )
        result.append(await read_competition(api_client, comp.id))
    return result


async def make_all_passed(
    session: AsyncSession,
    api_client: ApiClient,
    competitions: list[CompetitionModel],
) -> list[CompetitionModel]:
    """Make all competitions with reg end in past."""
    now = datetime.now(tz=UTC)
    result = []
    for comp in competitions:
        await _update_competition_directly(
            session,
            comp.id,
            registration_start=now - timedelta(minutes=2),
            registration_end=now - timedelta(minutes=1),
            is_archived=False,
        )
        result.append(await read_competition(api_client, comp.id))
    return result


async def make_all_inactive(
    session: AsyncSession,
    api_client: ApiClient,
    competitions: list[CompetitionModel],
) -> list[CompetitionModel]:
    """Make all competitions inactive (reg start in future)."""
    now = datetime.now(tz=UTC)
    result = []
    for comp in competitions:
        reg_start = now + timedelta(days=7)
        reg_end = reg_start + timedelta(days=14)

        tf_start = comp.schedule.team_formation_start
        tf_end = comp.schedule.team_formation_end
        if tf_start is not None:
            tf_start = reg_end + timedelta(days=1)
            tf_end = tf_start + timedelta(days=3) if tf_end is not None else None

        await _update_competition_directly(
            session,
            comp.id,
            registration_start=reg_start,
            registration_end=reg_end,
            is_archived=False,
            team_formation_start=tf_start,
            team_formation_end=tf_end,
        )
        result.append(await read_competition(api_client, comp.id))
    return result


async def change_archived_state(
    session: AsyncSession,
    api_client: ApiClient,
    competitions: list[CompetitionModel],
    *,
    is_archived: bool = False,
) -> list[CompetitionModel]:
    """Make all competitions archived/not archived and return updated competitions."""
    result = []
    for comp in competitions:
        await _update_competition_directly(
            session,
            comp.id,
            is_archived=is_archived,
        )
        result.append(await read_competition(api_client, comp.id))
    return result


async def create_mixed_competitions(
    session: AsyncSession,
    api_client: ApiClient,
    competitions: list[CompetitionModel],
) -> list[CompetitionModel]:
    """Create mixed competitions with different states (active, inactive, archived, not archived).

    Distribution:
    - 40% active (registration started), not archived
    - 30% inactive (registration not started), not archived
    - 20% passed (registration ended), not archived
    - 10% archived
    """
    if not competitions:
        return []

    num_competitions = len(competitions)
    shuffled = competitions.copy()
    random.shuffle(shuffled)

    num_active = max(1, int(num_competitions * 0.4))
    num_inactive = max(1, int(num_competitions * 0.3))
    num_passed = max(1, int(num_competitions * 0.2))

    active_comps = shuffled[:num_active]
    inactive_comps = shuffled[num_active : num_active + num_inactive]
    passed_comps = shuffled[num_active + num_inactive : num_active + num_inactive + num_passed]
    archived_comps = shuffled[num_active + num_inactive + num_passed :]

    updated_active = await make_all_active(session, api_client, active_comps)
    updated_passed = await make_all_passed(session, api_client, passed_comps)
    updated_archived = await change_archived_state(session, api_client, archived_comps, is_archived=True)

    return updated_active + inactive_comps + updated_passed + updated_archived


async def activate_competition(
    api_client: ApiClient,
    session: AsyncSession,
    update_competition_form_factory: UpdateCompetitionFormFactory,
    competition_id: CompetitionId,
    *,
    domains: list[Domain],
    auto_accept: bool = False,
    participant_type: ParticipantType = ParticipantType.ANY,
    max_participants: int = 10000,
) -> None:
    """Open the registration window of an existing competition and update its key fields.

    Uses ``make_all_active`` (DB-level) to move ``registration_start`` into the past, then
    calls the competition update API to set ``participant_type``, ``participant_limits``,
    ``is_archived``, ``domains``, and ``auto_accept``.
    """
    competition_model = await read_competition(api_client, competition_id)
    await make_all_active(session, api_client, [competition_model])

    update_form = update_competition_form_factory.build(
        participant_type=participant_type,
        participant_limits=ParticipantLimits(max=max_participants, min=1),
        is_archived=False,
        domains=domains,
        auto_accept=auto_accept,
    )
    with api_client.authenticate(auth_user_id=USER_ID):
        ((await api_client.update_competition(competition_id, update_form.model_dump(mode="json"))).assert_status(200))


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


def competition_form_to_model(
    competition_id: CompetitionId,
    organizer_id: OrganizerId,
    created_at: datetime,
    updated_at: datetime,
    form: CompetitionForm,
    clock: Clock,
) -> CompetitionModel:
    """Transform competition form and additional data to CompetitionModel."""
    return CompetitionModel(
        id=competition_id,
        organizer_id=organizer_id,
        title=form.title,
        banner=None,
        description=form.description,
        schedule=schedule_factory(form.schedule, clock),
        participant_limits=form.participant_limits,
        domains=form.domains,
        participant_type=form.participant_type,
        venue=form.venue,
        team_size=form.team_size,
        milestones=[
            Milestone(timestamp=milestone.timestamp, title=milestone.title)
            for milestone in sorted(form.milestones, key=lambda item: item.timestamp)
        ],
        auto_accept=form.auto_accept,
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
    clock: Clock,
) -> CompetitionModel:
    """Transform competition form and additional data to CompetitionModel."""
    return CompetitionModel(
        id=competition_id,
        organizer_id=organizer_id,
        title=form.title,
        banner=None,
        description=form.description,
        schedule=schedule_factory(form.schedule, clock),
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
        auto_accept=form.auto_accept,
        is_archived=form.is_archived,
        created_at=created_at,
        updated_at=updated_at,
    )


def competitions_list_to_preview_list(
    lst: CompetitionsList,
    organizer_form: OrganizerForm,
    organizer_id: OrganizerId,
) -> PreviewCompetitionsList:
    """Transform CompetitionsList to PreviewCompetitionsList with organizer info."""
    organizer_model = PreviewOrganizerModel(
        id=organizer_id,
        name=organizer_form.organizer_name,
        avatar_url=None,
    )

    preview_items = [
        PreviewCompetitionModel(
            id=comp.id,
            organizer=organizer_model,
            title=comp.title,
            banner=comp.banner,
            description=comp.description,
            schedule=comp.schedule,
            participant_limits=comp.participant_limits,
            domains=comp.domains,
            participant_type=comp.participant_type,
            venue=comp.venue,
            team_size=comp.team_size,
            milestones=comp.milestones,
            auto_accept=comp.auto_accept,
            is_archived=comp.is_archived,
            created_at=comp.created_at,
            updated_at=comp.updated_at,
        )
        for comp in lst.items
    ]

    return PreviewCompetitionsList(total=lst.total, page=lst.page, items=preview_items)
