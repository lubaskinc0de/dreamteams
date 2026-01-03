from collections.abc import Callable
from datetime import datetime

from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_competitions.list import PAGE_SIZE, CompetitionsList
from dreamteams.application.manage_competitions.read import CompetitionModel
from dreamteams.entities.common.identifiers import CompetitionId


def create_competitions_list(
    competitions: list[CompetitionModel],
    sort_by: CompetitionSortBy,
    sort_order: SortOrder,
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> CompetitionsList:
    """Create ``CompetitionsList`` from ``list[CompetitionModel]`` with sorting and pagination applied."""
    sort_key_mapping: dict[CompetitionSortBy, Callable[[CompetitionModel], tuple[datetime | str, CompetitionId]]] = {
        CompetitionSortBy.CREATED_AT: lambda c: (c.created_at, c.id),
        CompetitionSortBy.TITLE: lambda c: (c.title, c.id),
        CompetitionSortBy.REGISTRATION_START: lambda c: (c.schedule.registration_start, c.id),
    }

    sorted_items = sorted(
        competitions,
        key=sort_key_mapping[sort_by],
        reverse=(sort_order == SortOrder.DESC),
    )

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = sorted_items[start_idx:end_idx]

    return CompetitionsList(
        items=paginated_items,
        total=len(competitions),
        page=page,
    )
