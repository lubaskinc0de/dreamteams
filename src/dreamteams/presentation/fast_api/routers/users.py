from typing import BinaryIO

import filetype
import structlog
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, UploadFile

from dreamteams.application.common.logger import Logger
from dreamteams.application.manage_profile import ProfileModel, ReadProfile
from dreamteams.application.manage_profile.attach_avatar import AttachAvatar, AvatarForm
from dreamteams.application.manage_profile.delete import DeleteProfile
from dreamteams.application.manage_profile.detach_avatar import DetachAvatar
from dreamteams.presentation.fast_api.errors import InvalidAvatarError

logger: Logger = structlog.get_logger(__name__)
router = APIRouter(
    tags=["Users"],
    route_class=DishkaRoute,
    prefix="/users",
)


def is_valid_image(file_stream: BinaryIO) -> bool:
    """Checks image using filetype."""
    position = file_stream.tell()
    file_stream.seek(0)
    kind = filetype.guess(file_stream)
    file_stream.seek(position)
    return kind is not None and kind.mime.startswith("image/")


@router.get("/me")
async def view_profile(
    interactor: FromDishka[ReadProfile],
) -> ProfileModel:
    """HTTP endpoint for viewing user profile."""
    return await interactor.execute()


@router.delete("/me")
async def delete_profile(
    interactor: FromDishka[DeleteProfile],
) -> None:
    """HTTP endpoint for deleting user profile."""
    await interactor.execute()


@router.put("/me/avatar")
async def attach_avatar(
    interactor: FromDishka[AttachAvatar],
    file: UploadFile,
) -> None:
    """HTTP endpoint for attaching user avatar."""
    if file.content_type is None:
        logger.debug("File is rejected due to content type")
        raise InvalidAvatarError(reason="Cannot recognize file content type")

    if file.filename == "" or file.filename is None:
        logger.debug("File is rejected due to filename")
        raise InvalidAvatarError(reason="File filename is empty")

    if not is_valid_image(file.file):
        logger.debug("File is rejected due to invalid image")
        raise InvalidAvatarError(reason="File is not a valid image.")

    await interactor.execute(AvatarForm(file.file, file.content_type))


@router.delete("/me/avatar")
async def detach_avatar(
    interactor: FromDishka[DetachAvatar],
) -> None:
    """HTTP endpoint for detaching user avatar."""
    await interactor.execute()
