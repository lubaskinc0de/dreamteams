from typing import override

from dreamteams.adapters.cache.common.competition_read_cache import CompetitionReadCache
from dreamteams.application.common.dto.competition import CompetitionModel
from dreamteams.application.common.dto.explore_competition import ExploreCompetitionModel
from dreamteams.application.common.dto.preview_competition import PreviewCompetitionModel
from dreamteams.application.common.gateway.competition import (
    CompetitionGateway,
    CompetitionSortBy,
    ExploreSortBy,
)
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.entities.common.identifiers import CompetitionId, CompetitionTagId, OrganizerId, ParticipantId
from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.competition.entity import Competition


class CachedCompetitionGateway(CompetitionGateway):
    """Competition gateway decorator backed by Redis for read-model methods."""

    def __init__(self, wrapped: CompetitionGateway, cache: CompetitionReadCache) -> None:
        self._wrapped = wrapped
        self._cache = cache

    @override
    async def get(
        self,
        competition_id: CompetitionId,
        *,
        eager_milestones: bool = False,
        eager_tags: bool = False,
        eager_tracks: bool = False,
        for_update: bool = False,
    ) -> Competition | None:
        """Delegate entity loading to the wrapped gateway."""
        return await self._wrapped.get(
            competition_id,
            eager_milestones=eager_milestones,
            eager_tags=eager_tags,
            eager_tracks=eager_tracks,
            for_update=for_update,
        )

    @override
    async def get_with_organizer(self, competition_id: CompetitionId) -> Competition | None:
        """Delegate entity loading to the wrapped gateway."""
        return await self._wrapped.get_with_organizer(competition_id)

    @override
    async def clear_milestones(self, competition_id: CompetitionId) -> None:
        """Delegate relationship deletion to the wrapped gateway."""
        await self._wrapped.clear_milestones(competition_id)

    @override
    async def clear_tracks(self, competition_id: CompetitionId) -> None:
        """Delegate relationship deletion to the wrapped gateway."""
        await self._wrapped.clear_tracks(competition_id)

    @override
    async def read(self, competition_id: CompetitionId) -> CompetitionModel | None:
        """Fetch a single competition read model, using cache for positive hits."""
        cached = await self._cache.get_read(competition_id)
        if cached is not None:
            return cached

        model = await self._wrapped.read(competition_id)
        if model is not None:
            await self._cache.set_read(competition_id, model)
        return model

    @override
    async def list_for_organizer(
        self,
        organizer_id: OrganizerId,
        *,
        page: int,
        page_size: int,
        sort_by: CompetitionSortBy,
        sort_order: SortOrder,
        is_archived: bool | None,
        search: str | None,
    ) -> tuple[list[CompetitionModel], int]:
        """Delegate organizer-specific listing to the wrapped gateway."""
        return await self._wrapped.list_for_organizer(
            organizer_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            is_archived=is_archived,
            search=search,
        )

    @override
    async def list_preview(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[PreviewCompetitionModel], int]:
        """Delegate anonymous preview listing to the wrapped gateway."""
        return await self._wrapped.list_preview(page=page, page_size=page_size)

    @override
    async def explore(
        self,
        *,
        participant_id: ParticipantId,
        participant_type: ParticipantType,
        page: int,
        page_size: int,
        sort_by: ExploreSortBy,
        search: str | None,
        min_team_size: int | None,
        max_team_size: int | None,
        auto_accept: bool | None,
        tag_ids: list[CompetitionTagId] | None,
    ) -> tuple[list[ExploreCompetitionModel], int]:
        """Delegate participant-specific listing to the wrapped gateway."""
        return await self._wrapped.explore(
            participant_id=participant_id,
            participant_type=participant_type,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            search=search,
            min_team_size=min_team_size,
            max_team_size=max_team_size,
            auto_accept=auto_accept,
            tag_ids=tag_ids,
        )
