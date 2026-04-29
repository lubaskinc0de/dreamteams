from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from dreamteams.application.manage_tags import (
    CompetitionTagInput,
    CompetitionTagsList,
    CreateCompetitionTag,
    DeleteCompetitionTag,
    ListCompetitionTags,
    ListCompetitionTagsInput,
    ReadCompetitionTag,
)
from dreamteams.application.view_tags import (
    CompetitionTagsList as ViewCompetitionTagsList,
)
from dreamteams.application.view_tags import (
    ListCompetitionTags as ViewCompetitionTags,
)
from dreamteams.application.view_tags import (
    ListCompetitionTagsInput as ViewCompetitionTagsInput,
)
from dreamteams.entities.common.identifiers import CompetitionTagId
from dreamteams.entities.competition.tag import CompetitionTag

admin_router = APIRouter(
    tags=["Admin Tags"],
    route_class=DishkaRoute,
    prefix="/admin/tags",
)

router = APIRouter(
    tags=["Tags"],
    route_class=DishkaRoute,
    prefix="/tags",
)


@admin_router.post("/")
async def create_tag(
    interactor: FromDishka[CreateCompetitionTag],
    data: CompetitionTagInput,
) -> CompetitionTag:
    """Create a competition tag. Admin only."""
    return await interactor.execute(data)


@admin_router.get("/")
async def list_tags_by_admin(
    interactor: FromDishka[ListCompetitionTags],
    input_data: Annotated[ListCompetitionTagsInput, Query()],
) -> CompetitionTagsList:
    """List competition tags. Admin only."""
    return await interactor.execute(input_data)


@admin_router.get("/{tag_id}")
async def read_tag(
    interactor: FromDishka[ReadCompetitionTag],
    tag_id: CompetitionTagId,
) -> CompetitionTag:
    """Read a competition tag. Admin only."""
    return await interactor.execute(tag_id)


@admin_router.delete("/{tag_id}")
async def delete_tag(
    interactor: FromDishka[DeleteCompetitionTag],
    tag_id: CompetitionTagId,
) -> None:
    """Delete a competition tag. Admin only."""
    await interactor.execute(tag_id)


@router.get("/")
async def list_tags(
    interactor: FromDishka[ViewCompetitionTags],
    input_data: Annotated[ViewCompetitionTagsInput, Query()],
) -> ViewCompetitionTagsList:
    """List competition tags as a participant or organizer."""
    return await interactor.execute(input_data)
