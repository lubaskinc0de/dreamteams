import random
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models import competition_table
from dreamteams.application.manage_competitions import CompetitionModel
from dreamteams.application.manage_competitions.list import CompetitionsList
from dreamteams.application.preview_competition.list import (
    PreviewCompetitionModel,
    PreviewCompetitionsList,
    PreviewOrganizerModel,
)
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm
from tests.integration.api_client import ApiClient
from tests.integration.manage_competitions.helpers import read_competition


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

    # Calculate splits
    num_active = max(1, int(num_competitions * 0.4))
    num_inactive = max(1, int(num_competitions * 0.3))
    num_passed = max(1, int(num_competitions * 0.2))

    # Split competitions
    active_comps = shuffled[:num_active]
    inactive_comps = shuffled[num_active : num_active + num_inactive]
    passed_comps = shuffled[num_active + num_inactive : num_active + num_inactive + num_passed]
    archived_comps = shuffled[num_active + num_inactive + num_passed :]

    # Apply transformations
    updated_active = await make_all_active(session, api_client, active_comps)
    updated_passed = await make_all_passed(session, api_client, passed_comps)
    updated_archived = await change_archived_state(session, api_client, archived_comps, is_archived=True)

    # Inactive competitions remain as they are (registration start in future)
    # Just return them as is
    return updated_active + inactive_comps + updated_passed + updated_archived


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
