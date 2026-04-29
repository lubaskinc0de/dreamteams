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
from dreamteams.adapters.metrics import (
    ApplicationAcceptedMetricsEventHandler,
    ApplicationFormCreatedMetricsEventHandler,
    ApplicationFormDeletedMetricsEventHandler,
    ApplicationRejectedMetricsEventHandler,
    ApplicationSubmittedMetricsEventHandler,
    ApplicationWithdrawnMetricsEventHandler,
    AvatarAttachedMetricsEventHandler,
    AvatarDetachedMetricsEventHandler,
    CompetitionCreatedMetricsEventHandler,
    RegistrationMetricsEventHandler,
)
from dreamteams.application.common.events import (
    ApplicationAccepted,
    ApplicationFormCreated,
    ApplicationFormDeleted,
    ApplicationRejected,
    ApplicationSubmitted,
    ApplicationWithdrawn,
    AvatarAttached,
    AvatarDetached,
    CompetitionChanged,
    CompetitionCreated,
    CompetitionDeleted,
    CompetitionTagCreated,
    CompetitionTagDeleted,
    DomainEvent,
    UserBlocked,
    UserRegistered,
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
    registration_metrics_handler: RegistrationMetricsEventHandler
    competition_created_metrics_handler: CompetitionCreatedMetricsEventHandler
    application_submitted_metrics_handler: ApplicationSubmittedMetricsEventHandler
    application_accepted_metrics_handler: ApplicationAcceptedMetricsEventHandler
    application_rejected_metrics_handler: ApplicationRejectedMetricsEventHandler
    application_withdrawn_metrics_handler: ApplicationWithdrawnMetricsEventHandler
    application_form_created_metrics_handler: ApplicationFormCreatedMetricsEventHandler
    application_form_deleted_metrics_handler: ApplicationFormDeletedMetricsEventHandler
    avatar_attached_metrics_handler: AvatarAttachedMetricsEventHandler
    avatar_detached_metrics_handler: AvatarDetachedMetricsEventHandler

    def as_mapping(self) -> Mapping[type[DomainEvent], tuple[EventHandler, ...]]:
        """Return event handlers keyed by supported event type."""
        return {
            UserRegistered: (self.registration_metrics_handler,),
            UserBlocked: (self.user_blocked_handler,),
            UserUnblocked: (self.user_unblocked_handler,),
            CompetitionCreated: (self.competition_handler, self.competition_created_metrics_handler),
            CompetitionChanged: (self.competition_handler,),
            CompetitionDeleted: (self.competition_handler,),
            CompetitionTagCreated: (self.competition_tag_handler,),
            CompetitionTagDeleted: (self.competition_tag_handler,),
            ApplicationFormCreated: (self.application_form_handler, self.application_form_created_metrics_handler),
            ApplicationFormDeleted: (self.application_form_handler, self.application_form_deleted_metrics_handler),
            ApplicationSubmitted: (self.application_submitted_metrics_handler,),
            ApplicationAccepted: (self.application_handler, self.application_accepted_metrics_handler),
            ApplicationRejected: (self.application_rejected_metrics_handler,),
            ApplicationWithdrawn: (self.application_withdrawn_metrics_handler,),
            AvatarAttached: (self.avatar_attached_metrics_handler,),
            AvatarDetached: (self.avatar_detached_metrics_handler,),
        }
