from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from dreamteams.application.issue_invite import (
    InviteIssued,
    InviteModel,
    InvitesList,
    IssueInvite,
    IssueInviteForm,
    ListInvites,
    ReadInvite,
    RevokeInvite,
)
from dreamteams.entities.common.identifiers import OrganizerInviteId

router = APIRouter(
    tags=["Invites"],
    route_class=DishkaRoute,
    prefix="/invites",
)


@router.post("/")
async def issue_invite(
    interactor: FromDishka[IssueInvite],
    data: IssueInviteForm,
) -> InviteIssued:
    """HTTP endpoint for issuing a new organizer invite code. Admin only."""
    return await interactor.execute(data=data)


@router.get("/")
async def list_invites(
    interactor: FromDishka[ListInvites],
    page: int = 1,
) -> InvitesList:
    """HTTP endpoint for listing organizer invites. Admin only."""
    return await interactor.execute(page=page)


@router.get("/{invite_id}")
async def read_invite(
    interactor: FromDishka[ReadInvite],
    invite_id: OrganizerInviteId,
) -> InviteModel:
    """HTTP endpoint for reading a single organizer invite by ID. Admin only."""
    return await interactor.execute(invite_id=invite_id)


@router.delete("/{invite_id}")
async def revoke_invite(
    interactor: FromDishka[RevokeInvite],
    invite_id: OrganizerInviteId,
) -> None:
    """HTTP endpoint for revoking an organizer invite. Admin only."""
    await interactor.execute(invite_id=invite_id)
