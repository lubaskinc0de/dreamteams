import structlog
from opentelemetry import trace
from pydantic import BaseModel, EmailStr, Field

from dreamteams.application.common.gateway.organizer import OrganizerGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.common.uow import UoW
from dreamteams.application.errors.organizer import OrganizerAlreadyExistsError, OrganizerNotFoundError
from dreamteams.entities.user import UpdateOrganizerData

logger: Logger = structlog.get_logger(__name__)
_tracer = trace.get_tracer("dreamteams.interactors")


class UpdateOrganizerForm(BaseModel):
    """Form for updating ``Organizer`` profile."""

    organizer_name: str = Field(max_length=70)
    contact_email: EmailStr


@interactor
class UpdateOrganizer:
    """Interactor for updating ``Organizer`` profile."""

    uow: UoW
    idp: IdProvider
    organizer_gateway: OrganizerGateway

    async def execute(self, data: UpdateOrganizerForm) -> None:
        """Update organizer profile fields."""
        with _tracer.start_as_current_span("interactor.update_organizer"):
            user = await self.idp.get_user()

            if user.organizer is None:
                raise OrganizerNotFoundError

            logger.debug("Updating organizer profile", user_id=user.id)

            email_changed = data.contact_email != user.organizer.contact_email
            if email_changed and not await self.organizer_gateway.is_unique_by_email(data.contact_email):
                raise OrganizerAlreadyExistsError

            user.organizer.update(
                UpdateOrganizerData(
                    organizer_name=data.organizer_name,
                    contact_email=data.contact_email,
                ),
            )
            await self.uow.commit()

            logger.info("Organizer profile updated", user_id=user.id)
