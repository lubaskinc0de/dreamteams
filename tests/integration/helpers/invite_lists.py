from dreamteams.application.issue_invite import InviteModel, InvitesList
from dreamteams.application.view_issued_invites.list_invites import PAGE_SIZE


def create_invites_list(
    invites: list[InviteModel],
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> InvitesList:
    """Create ``InvitesList`` from ``list[InviteModel]`` with pagination applied."""
    start = (page - 1) * page_size
    end = start + page_size
    return InvitesList(items=invites[start:end], total=len(invites), page=page)
