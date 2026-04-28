"""Gateway for creating organizer users via the API."""

from dataclasses import dataclass
from uuid import uuid4

from faker import Faker

from tests.common.factory.organizer import OrganizerFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.helpers.admin_factory import AdminGateway
from tests.integration.helpers.models import OrganizerCreated, OrganizerWithAdmin


@dataclass
class OrganizerGateway:
    """Gateway for organizer registration in tests."""

    api_client: ApiClient
    organizer_form_factory: OrganizerFormFactory
    faker: Faker

    async def create_with_invite(self, invite_code: str, *, organizer_name: str | None = None) -> OrganizerCreated:
        """Register a fresh organizer using an existing invite code."""
        auth_id = str(uuid4())
        email = self.faker.email()
        form = (
            self.organizer_form_factory.build(invite_code=invite_code)
            if organizer_name is None
            else self.organizer_form_factory.build(invite_code=invite_code, organizer_name=organizer_name)
        )

        with self.api_client.authenticate(auth_user_id=auth_id, auth_user_email=email):
            organizer = (
                (await self.api_client.register_organizer(form.model_dump())).assert_status(200).ensure_content()
            )

        return OrganizerCreated(auth_id=auth_id, email=email, form=form, created=organizer)

    async def create(self, admin_auth_id: str, *, organizer_name: str | None = None) -> OrganizerCreated:
        """Issue a fresh invite as admin and register a new organizer."""
        with self.api_client.authenticate(auth_user_id=admin_auth_id):
            invite = (await self.api_client.issue_invite({})).assert_status(200).ensure_content()

        return await self.create_with_invite(invite.code, organizer_name=organizer_name)

    async def create_with_admin(self, admin_gateway: AdminGateway) -> OrganizerWithAdmin:
        """Create a fresh admin and then register an organizer under them."""
        admin = await admin_gateway.create()
        organizer = await self.create(admin.auth_id)

        return OrganizerWithAdmin(admin=admin, organizer=organizer)
