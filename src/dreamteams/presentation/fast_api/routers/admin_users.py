from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from dreamteams.application.manage_users import BlockUser, BlockUserForm, UnblockUser, UnblockUserForm
from dreamteams.entities.common.identifiers import UserId

router = APIRouter(
    tags=["Admin Users"],
    route_class=DishkaRoute,
    prefix="/admin/users",
)


@router.post("/{user_id}/block")
async def block_user(
    interactor: FromDishka[BlockUser],
    user_id: UserId,
    data: BlockUserForm,
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
