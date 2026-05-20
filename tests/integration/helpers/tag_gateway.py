"""Gateway for creating competition tags via the API."""

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import uuid4

from dreamteams.application.manage_tags import CompetitionTagInput
from dreamteams.entities.competition.tag import CompetitionTag
from tests.integration.api_client import ApiClient


@dataclass
class TagGateway:
    """Gateway for admin-managed competition tags in tests."""

    api_client: ApiClient

    async def create_many(self, admin_auth_id: str, values: Sequence[str]) -> list[CompetitionTag]:
        """Create multiple tags as admin."""
        with self.api_client.authenticate(auth_user_id=admin_auth_id):
            responses = await asyncio.gather(
                *[
                    self.api_client.create_tag(CompetitionTagInput(value=value).model_dump(mode="json"))
                    for value in values
                ],
            )
        return [response.assert_status(200).ensure_content() for response in responses]

    async def create_many_unique(self, admin_auth_id: str, prefixes: Sequence[str]) -> list[CompetitionTag]:
        """Create multiple tags with unique values based on readable prefixes."""
        return await self.create_many(
            admin_auth_id,
            [f"{prefix}-{uuid4()}" for prefix in prefixes],
        )
