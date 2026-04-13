from datetime import datetime
from typing import Any

import structlog
from pydantic import BaseModel

from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.application import ApplicationNotFoundError
from dreamteams.entities.application.entity import ApplicationStatus
from dreamteams.entities.common.identifiers import ApplicationId, CompetitionId, ParticipantId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.errors.base import AccessDeniedError

logger: Logger = structlog.get_logger(__name__)


class ApplicationModel(BaseModel):
    """Full representation of a registration application."""

    id: ApplicationId
    participant_id: ParticipantId
    competition_id: CompetitionId
    domains: list[Domain]
    status: ApplicationStatus
    created_at: datetime
    form_data: dict[str, Any] | None


@interactor
class ReadMyApplication:
    """Interactor for reading a single application owned by the current participant."""

    idp: IdProvider
    application_gateway: ApplicationGateway

    async def execute(self, application_id: ApplicationId) -> ApplicationModel:
        """Read a single application; only the submitting participant may access it."""
        user = await self.idp.get_user()
        logger.debug("Reading own application", application_id=application_id, user_id=user.id)

        application = await self.application_gateway.get(application_id)
        if application is None:
            logger.warning("Application not found", application_id=application_id, user_id=user.id)
            raise ApplicationNotFoundError

        if user.participant is None or user.participant.id != application.participant_id:
            logger.warning("Access denied to read application", application_id=application_id, user_id=user.id)
            raise AccessDeniedError(message="Only the participant who submitted this application can read it")

        return ApplicationModel(
            id=application.id,
            participant_id=application.participant_id,
            competition_id=application.competition_id,
            domains=application.domains,
            status=application.status,
            created_at=application.created_at,
            form_data=application.form_data,
        )
