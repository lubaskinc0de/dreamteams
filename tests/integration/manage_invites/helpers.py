import asyncio

from dreamteams.application.manage_invites import InviteModel, InvitesList
from dreamteams.application.manage_invites.list import PAGE_SIZE
from tests.integration.api_client import ApiClient
from tests.integration.constants import ADMIN_USER_ID


def create_invites_list(
    invites: list[InviteModel],
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> InvitesList:
    """Create ``InvitesList`` from ``list[InviteModel]`` with pagination applied."""
    start = (page - 1) * page_size
    end = start + page_size
    return InvitesList(items=invites[start:end], total=len(invites), page=page)


async def create_invites(num_invites: int, api_client: ApiClient) -> list[InviteModel]:
    """Issue N invites as admin and return all as InviteModel sorted by created_at DESC."""
    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        issue_responses = await asyncio.gather(*[api_client.issue_invite({}) for _ in range(num_invites)])
    issued = [r.assert_status(200).ensure_content() for r in issue_responses]

    with api_client.authenticate(auth_user_id=ADMIN_USER_ID):
        read_responses = await asyncio.gather(*[api_client.read_invite(i.invite_id) for i in issued])
    invites = [r.assert_status(200).ensure_content() for r in read_responses]

    return sorted(invites, key=lambda i: i.created_at, reverse=True)
