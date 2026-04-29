from collections.abc import Mapping
from dataclasses import dataclass

from dreamteams.adapters.cache.event_handler import (
    ApplicationCacheEventHandler,
    ApplicationFormCacheEventHandler,
    CompetitionCacheEventHandler,
    CompetitionTagCacheEventHandler,
    UserBlockedCacheEventHandler,
    UserUnblockedCacheEventHandler,
)
from dreamteams.adapters.event_bus import EventHandler
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


@dataclass(frozen=True, slots=True)
class EventHandlersRegistry:
    """Registry of event handlers by event class."""

    user_blocked_handler: UserBlockedCacheEventHandler
    user_unblocked_handler: UserUnblockedCacheEventHandler
    competition_handler: CompetitionCacheEventHandler
    competition_tag_handler: CompetitionTagCacheEventHandler
    application_form_handler: ApplicationFormCacheEventHandler
    application_handler: ApplicationCacheEventHandler

    def as_mapping(self) -> Mapping[type[DomainEvent], tuple[EventHandler, ...]]:
        """Return event handlers keyed by supported event type."""
        return {
            UserBlocked: (self.user_blocked_handler,),
            UserUnblocked: (self.user_unblocked_handler,),
            CompetitionCreated: (self.competition_handler,),
            CompetitionChanged: (self.competition_handler,),
            CompetitionDeleted: (self.competition_handler,),
            CompetitionTagCreated: (self.competition_tag_handler,),
            CompetitionTagDeleted: (self.competition_tag_handler,),
            ApplicationFormCreated: (self.application_form_handler,),
            ApplicationFormDeleted: (self.application_form_handler,),
            ApplicationAccepted: (self.application_handler,),
        }
