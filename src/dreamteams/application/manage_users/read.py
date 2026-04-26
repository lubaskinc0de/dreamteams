import structlog
from pydantic import BaseModel

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.gateway.user import UserGateway
from dreamteams.application.common.idp import IdProvider
from dreamteams.application.common.interactor import interactor
from dreamteams.application.common.logger import Logger
from dreamteams.application.errors.user import UserNotFoundError
from dreamteams.application.manage_users.models import AdminOrganizerModel, AdminParticipantModel, AdminUserModel
from dreamteams.application.manage_users.shared import ensure_admin
from dreamteams.entities.common.identifiers import UserId

logger: Logger = structlog.get_logger(__name__)


class AdminUserDetails(BaseModel):
    """Full admin-facing user details."""

    user: AdminUserModel
    organizer: AdminOrganizerModel | None
    participant: AdminParticipantModel | None


@interactor
class ReadUserByAdmin:
    """Interactor for reading full user details as an admin."""

    idp: IdProvider
    user_gateway: UserGateway
    avatar_storage: AvatarStorage

    async def execute(self, user_id: UserId) -> AdminUserDetails:
        """Read full target user details."""
        admin_user_id = await self.idp.get_user_id()
        admin = await self.user_gateway.get(admin_user_id)
        ensure_admin(admin, admin_user_id)

        target = await self.user_gateway.get_with_roles(user_id)
        if target is None:
            raise UserNotFoundError(user_id=user_id)

        logger.debug("Reading user by admin", admin_user_id=admin_user_id, target_user_id=user_id)

        organizer = target.organizer
        participant = target.participant
        return AdminUserDetails(
            user=AdminUserModel(
                id=target.id,
                avatar_url=self.avatar_storage.get_url(target.avatar) if target.avatar is not None else None,
                is_admin=target.is_admin,
                ban_status=target.ban_status,
            ),
            organizer=(
                AdminOrganizerModel(
                    id=organizer.id,
                    user_id=organizer.user_id,
                    organizer_name=organizer.organizer_name,
                    phone_number=organizer.phone_number,
                    contact_email=organizer.contact_email,
                )
                if organizer is not None
                else None
            ),
            participant=(
                AdminParticipantModel(
                    id=participant.id,
                    user_id=participant.user_id,
                    full_name=participant.full_name,
                    participant_type=participant.participant_type,
                    age=participant.age.value,
                    bio=participant.bio,
                    skills=participant.skills,
                    experience_level=participant.experience_level,
                    preferred_domains=participant.preferred_domains,
                    contacts=participant.contacts,
                    created_at=participant.created_at,
                    updated_at=participant.updated_at,
                )
                if participant is not None
                else None
            ),
        )
