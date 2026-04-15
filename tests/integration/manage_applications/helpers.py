from dreamteams.application.manage_applications import ApplicationsList
from dreamteams.application.manage_applications.list import PAGE_SIZE
from dreamteams.application.manage_my_applications import ApplicationModel


def create_applications_list(
    applications: list[ApplicationModel],
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> ApplicationsList:
    """Build paginated ``ApplicationsList`` from ``list[ApplicationModel]`` sorted by ``created_at`` descending."""
    sorted_items = sorted(applications, key=lambda a: a.created_at, reverse=True)
    start = (page - 1) * page_size
    paginated = sorted_items[start : start + page_size]
    return ApplicationsList(items=paginated, total=len(applications), page=page)
