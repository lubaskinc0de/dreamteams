"""Gateway for creating admin users and performing admin operations via the API."""

import asyncio
from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models.auth_user import auth_user_table
from dreamteams.adapters.db.models.user import user_table
from dreamteams.application.manage_invites import InviteModel
from tests.integration.api_client import ApiClient
from tests.integration.helpers.models import AdminCreated


@dataclass
class AdminGateway:
    """Gateway for creating admin users and issuing invites in tests."""

    session: AsyncSession
    api_client: ApiClient

    async def create(self) -> AdminCreated:
        """Insert a fresh admin user directly into the DB and return their credentials."""
        auth_id = str(uuid4())
        user_id = uuid4()

        await self.session.execute(insert(user_table).values(id=user_id, avatar=None, is_admin=True))
        await self.session.execute(insert(auth_user_table).values(auth_user_id=auth_id, user_id=user_id))
        await self.session.commit()

        return AdminCreated(auth_id=auth_id, user_id=user_id)

    async def create_invites(self, admin_auth_id: str, n: int) -> list[InviteModel]:
        """Issue N invites as admin and return them as InviteModel sorted by created_at DESC."""
        with self.api_client.authenticate(auth_user_id=admin_auth_id):
            issue_responses = await asyncio.gather(*[self.api_client.issue_invite({}) for _ in range(n)])
        issued = [r.assert_status(200).ensure_content() for r in issue_responses]

        with self.api_client.authenticate(auth_user_id=admin_auth_id):
            read_responses = await asyncio.gather(*[self.api_client.read_invite(i.invite_id) for i in issued])
        invites = [r.assert_status(200).ensure_content() for r in read_responses]

        return sorted(invites, key=lambda i: i.created_at, reverse=True)
