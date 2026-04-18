from dreamteams.application.common.gateway.application import ApplicationSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.manage_applications import ApplicationsList
from dreamteams.application.manage_applications.list import PAGE_SIZE
from dreamteams.application.manage_my_applications import ApplicationModel
from dreamteams.entities.application.entity import ApplicationStatus


def create_applications_list(
    applications: list[ApplicationModel],
    page: int = 1,
    page_size: int = PAGE_SIZE,
    *,
    sort_by: ApplicationSortBy = ApplicationSortBy.CREATED_AT,
    sort_order: SortOrder = SortOrder.DESC,
    status: ApplicationStatus | None = None,
) -> ApplicationsList:
    """Build paginated ``ApplicationsList`` with the same sort/filter semantics as the gateway."""
    sort_key = {
        ApplicationSortBy.CREATED_AT: lambda a: (a.created_at, a.id),
    }[sort_by]

    filtered = [a for a in applications if status is None or a.status == status]
    sorted_items = sorted(filtered, key=sort_key, reverse=(sort_order == SortOrder.DESC))
    start = (page - 1) * page_size
    paginated = sorted_items[start : start + page_size]
    return ApplicationsList(items=paginated, total=len(filtered), page=page)
