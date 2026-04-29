from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query
from pydantic import BaseModel

from dreamteams.application.block_user import (
    AdminUserDetails,
    BlockUser,
    BlockUserForm,
    ListUsers,
    ListUsersInput,
    ReadUserByAdmin,
    UnblockUser,
    UnblockUserForm,
    UsersList,
)
from dreamteams.entities.common.identifiers import UserId

router = APIRouter(
    tags=["Admin Users"],
    route_class=DishkaRoute,
    prefix="/admin/users",
)


class BlockUserRequest(BaseModel):
    """Request body for blocking a user account."""

    reason: str | None = None


@router.get("/")
async def list_users(
    interactor: FromDishka[ListUsers],
    input_data: Annotated[ListUsersInput, Query()],
) -> UsersList:
    """List users. Admin only."""
    return await interactor.execute(input_data)


@router.get("/{user_id}")
async def read_user(
    interactor: FromDishka[ReadUserByAdmin],
    user_id: UserId,
) -> AdminUserDetails:
    """Read full user details. Admin only."""
    return await interactor.execute(user_id)


@router.post("/{user_id}/block")
async def block_user(
    interactor: FromDishka[BlockUser],
    user_id: UserId,
    data: BlockUserRequest,
) -> None:
    """Block a user account. Admin only."""
    await interactor.execute(BlockUserForm(target_user_id=user_id, reason=data.reason))


@router.post("/{user_id}/unblock")
async def unblock_user(
    interactor: FromDishka[UnblockUser],
    user_id: UserId,
) -> None:
    """Unblock a user account. Admin only."""
    await interactor.execute(UnblockUserForm(target_user_id=user_id))
