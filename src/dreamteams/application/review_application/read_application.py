import structlog

from dreamteams.application.common.dto.application import ApplicationModel, ParticipantInfo
from dreamteams.application.common.gateway.application import ApplicationGateway
from dreamteams.application.common.gateway.competition import CompetitionGateway
from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.gateway.participant import ParticipantGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.errors.application import ApplicationNotFoundError
from dreamteams.application.errors.organizer import OrganizerNotFoundError
from dreamteams.entities.common.identifiers import ApplicationId
from dreamteams.entities.errors.base import AccessDeniedError
from dreamteams_common.interactor import interactor
from dreamteams_common.logger import Logger

logger: Logger = structlog.get_logger(__name__)


@interactor
class ReadApplication:
    """Interactor for reading a single application (organizer access)."""

    idp: IdProvider
    organizer_gateway: OrganizerGateway
    application_gateway: ApplicationGateway
    competition_gateway: CompetitionGateway
    participant_gateway: ParticipantGateway

    async def execute(self, application_id: ApplicationId) -> ApplicationModel:
        """Read a single application; only the organizer who owns the competition may access it."""
        user_id = await self.idp.get_user_id()
        logger.debug("Reading application", application_id=application_id, user_id=user_id)

        application = await self.application_gateway.get(application_id)
        if application is None:
            logger.warning("Application not found", application_id=application_id, user_id=user_id)
            raise ApplicationNotFoundError

        competition = await self.competition_gateway.get(application.competition_id)
        organizer = await self.organizer_gateway.get_by_user_id(user_id)
        if organizer is None:
            raise OrganizerNotFoundError
        if competition is None or not competition.is_owned_by(organizer):
            logger.warning("Access denied to read application", application_id=application_id, user_id=user_id)
            raise AccessDeniedError(
                message="Only the organizer who owns this competition can read its applications",
            )

        participant = await self.participant_gateway.get(application.participant_id, eager_skills_and_contacts=True)
        if participant is None:
            raise ApplicationNotFoundError

        return ApplicationModel(
            id=application.id,
            competition_id=application.competition_id,
            competition_name=competition.title,
            track=application.track,
            status=application.status,
            created_at=application.created_at,
            form_data=application.form_data,
            participant=ParticipantInfo(
                id=participant.id,
                full_name=participant.full_name,
                bio=participant.bio,
                participant_type=participant.participant_type,
                age=participant.age.value,
                skills=participant.skills,
                experience_level=participant.experience_level,
                contacts=participant.contacts,
            ),
        )
