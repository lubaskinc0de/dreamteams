from dreamteams.adapters.cache.common.application_form_cache import ApplicationFormCache
from dreamteams.adapters.cache.common.blocked_user_cache import BlockedUserCache
from dreamteams.adapters.cache.common.competition_read_cache import CompetitionReadCache
from dreamteams.adapters.cache.common.competition_tag_read_cache import CompetitionTagReadCache
from dreamteams.application.common.events import (
    ApplicationAccepted,
    ApplicationFormCreated,
    ApplicationFormDeleted,
    CompetitionChanged,
    CompetitionCreated,
    CompetitionDeleted,
    CompetitionTagCreated,
    CompetitionTagDeleted,
    DomainEvent,
    UserBlocked,
    UserUnblocked,
)


class UserBlockedCacheEventHandler:
    """Applies cache updates for a user-blocked event."""

    def __init__(
        self,
        blocked_user_cache: BlockedUserCache,
        application_form_cache: ApplicationFormCache,
        competition_cache: CompetitionReadCache,
    ) -> None:
        self._blocked_user_cache = blocked_user_cache
        self._application_form_cache = application_form_cache
        self._competition_cache = competition_cache

    async def __call__(self, event: DomainEvent) -> None:
        """Handle cache consequences of the event."""
        if not isinstance(event, UserBlocked):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)

        await self._blocked_user_cache.set_blocked(event.user_id, event.ban_status)
        await self._application_form_cache.clear()
        await self._competition_cache.clear_read()


class UserUnblockedCacheEventHandler:
    """Applies cache updates for a user-unblocked event."""

    def __init__(
        self,
        blocked_user_cache: BlockedUserCache,
        application_form_cache: ApplicationFormCache,
        competition_cache: CompetitionReadCache,
    ) -> None:
        self._blocked_user_cache = blocked_user_cache
        self._application_form_cache = application_form_cache
        self._competition_cache = competition_cache

    async def __call__(self, event: DomainEvent) -> None:
        """Handle cache consequences of the event."""
        if not isinstance(event, UserUnblocked):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)

        await self._blocked_user_cache.delete(event.user_id)
        await self._application_form_cache.clear()
        await self._competition_cache.clear_read()


class CompetitionCacheEventHandler:
    """Invalidates cached single-competition read models."""

    def __init__(self, competition_cache: CompetitionReadCache) -> None:
        self._competition_cache = competition_cache

    async def __call__(self, event: DomainEvent) -> None:
        """Handle cache consequences of the event."""
        if not isinstance(event, CompetitionCreated | CompetitionChanged | CompetitionDeleted):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)

        await self._competition_cache.delete_read(event.competition_id)


class CompetitionTagCacheEventHandler:
    """Invalidates caches derived from competition tags."""

    def __init__(
        self,
        competition_tag_cache: CompetitionTagReadCache,
        competition_cache: CompetitionReadCache,
    ) -> None:
        self._competition_tag_cache = competition_tag_cache
        self._competition_cache = competition_cache

    async def __call__(self, event: DomainEvent) -> None:
        """Handle cache consequences of the event."""
        if not isinstance(event, CompetitionTagCreated | CompetitionTagDeleted):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)

        await self._competition_tag_cache.clear()
        await self._competition_cache.clear_read()


class ApplicationFormCacheEventHandler:
    """Invalidates cached application forms."""

    def __init__(self, application_form_cache: ApplicationFormCache) -> None:
        self._application_form_cache = application_form_cache

    async def __call__(self, event: DomainEvent) -> None:
        """Handle cache consequences of the event."""
        if not isinstance(event, ApplicationFormCreated | ApplicationFormDeleted):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)

        await self._application_form_cache.delete(event.competition_id)


class ApplicationCacheEventHandler:
    """Invalidates cached competition reads affected by application lifecycle changes."""

    def __init__(self, competition_cache: CompetitionReadCache) -> None:
        self._competition_cache = competition_cache

    async def __call__(self, event: DomainEvent) -> None:
        """Handle cache consequences of the event."""
        if not isinstance(event, ApplicationAccepted):
            msg = f"{type(self).__name__} received invalid event: {type(event).__name__}"
            raise TypeError(msg)

        await self._competition_cache.delete_read(event.competition_id)
