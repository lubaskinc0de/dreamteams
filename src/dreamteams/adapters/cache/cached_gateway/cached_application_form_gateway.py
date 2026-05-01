from typing import override

from dreamteams.adapters.cache.common.application_form_cache import ApplicationFormCache
from dreamteams.application.common.gateway.application_form import ApplicationFormGateway
from dreamteams.entities.application_form.entity import ApplicationForm
from dreamteams.entities.common.identifiers import ApplicationFormId, CompetitionId


class CachedApplicationFormGateway(ApplicationFormGateway):
    """Application form gateway decorator for read-through cache access."""

    def __init__(
        self,
        wrapped: ApplicationFormGateway,
        cache: ApplicationFormCache,
    ) -> None:
        self._wrapped = wrapped
        self._cache = cache

    @override
    async def get_by_competition_id(self, competition_id: CompetitionId) -> ApplicationForm | None:
        """Fetch an application form by competition id, using cache for positive hits."""
        cached = await self._cache.get(competition_id)
        if cached is not None:
            return cached

        form = await self._wrapped.get_by_competition_id(competition_id)
        if form is not None:
            await self._cache.set(competition_id, form)
        return form

    @override
    async def delete_by_id(self, entity_id: ApplicationFormId) -> None:
        """Delete application form by id."""
        return await self._wrapped.delete_by_id(entity_id)
