"""Gateway for creating and managing competition entities via the API."""

import asyncio
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from dreamteams.adapters.db.models import competition_table
from dreamteams.application.common.dto.competition_track import CompetitionTrackForm
from dreamteams.application.common.dto.milestone import MilestoneForm
from dreamteams.application.delete_competition import CompetitionModel
from dreamteams.application.publish_competition.publish_competition import CompetitionForm
from dreamteams.application.update_my_competition.update import UpdateCompetitionForm
from dreamteams.entities.common.identifiers import CompetitionId, CompetitionTagId
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import ScheduleData
from tests.common.factory.competition import CompetitionFormFactory, UpdateCompetitionFormFactory
from tests.integration.api_client import ApiClient
from tests.integration.helpers.models import CompetitionCreated


@dataclass
class CompetitionGateway:
    """Gateway for creating, reading and state-managing competitions in tests."""

    api_client: ApiClient
    session: AsyncSession
    competition_form_factory: CompetitionFormFactory
    update_competition_form_factory: UpdateCompetitionFormFactory

    # --- Direct DB helpers ---

    async def _update_directly(self, competition_id: CompetitionId, **values: Any) -> None:
        """Update competition fields directly in the database, bypassing entity rules."""
        values["updated_at"] = datetime.now(tz=UTC)
        await self.session.execute(
            update(competition_table).where(competition_table.c.id == competition_id).values(**values),
        )
        await self.session.commit()

    # --- Read / update via API ---

    async def read(self, competition_id: CompetitionId, organizer_auth_id: str) -> CompetitionModel:
        """Read a competition via API."""
        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            return (await self.api_client.read_competition(competition_id)).assert_status(200).ensure_content()

    async def update(
        self,
        competition_id: CompetitionId,
        data: UpdateCompetitionForm,
        organizer_auth_id: str,
    ) -> CompetitionModel:
        """Update competition and return the updated model."""
        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            (await self.api_client.update_competition(competition_id, data.model_dump(mode="json"))).assert_status(200)
            return (await self.api_client.read_competition(competition_id)).assert_status(200).ensure_content()

    # --- State manipulation ---

    async def _read_many(
        self,
        competition_ids: list[CompetitionId],
        organizer_auth_id: str,
    ) -> list[CompetitionModel]:
        """Read multiple competitions in parallel."""
        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            responses = await asyncio.gather(
                *[self.api_client.read_competition(cid) for cid in competition_ids],
            )
        return [r.assert_status(200).ensure_content() for r in responses]

    async def make_all_active(
        self,
        competitions: list[CompetitionModel],
        organizer_auth_id: str,
    ) -> list[CompetitionModel]:
        """Make all competitions active (reg started, reg not ended, not archived)."""
        now = datetime.now(tz=UTC)
        for comp in competitions:
            reg_end = comp.schedule.registration_end
            if reg_end <= now:
                reg_end = now + timedelta(days=7)

            tf_start = comp.schedule.team_formation_start
            tf_end = comp.schedule.team_formation_end
            if tf_start is not None and tf_start <= reg_end:
                tf_start = reg_end + timedelta(days=1)
                tf_end = tf_start + timedelta(days=3) if tf_end is not None else None

            await self._update_directly(
                comp.id,
                registration_start=now - timedelta(minutes=1),
                registration_end=reg_end,
                is_archived=False,
                team_formation_start=tf_start,
                team_formation_end=tf_end,
            )

        return await self._read_many([c.id for c in competitions], organizer_auth_id)

    async def make_all_passed(
        self,
        competitions: list[CompetitionModel],
        organizer_auth_id: str,
    ) -> list[CompetitionModel]:
        """Make all competitions with registration end in the past."""
        now = datetime.now(tz=UTC)
        for comp in competitions:
            await self._update_directly(
                comp.id,
                registration_start=now - timedelta(minutes=2),
                registration_end=now - timedelta(minutes=1),
                is_archived=False,
            )

        return await self._read_many([c.id for c in competitions], organizer_auth_id)

    async def make_all_inactive(
        self,
        competitions: list[CompetitionModel],
        organizer_auth_id: str,
    ) -> list[CompetitionModel]:
        """Make all competitions inactive (registration start in future)."""
        now = datetime.now(tz=UTC)
        for comp in competitions:
            reg_start = now + timedelta(days=7)
            reg_end = reg_start + timedelta(days=14)

            tf_start = comp.schedule.team_formation_start
            tf_end = comp.schedule.team_formation_end
            if tf_start is not None:
                tf_start = reg_end + timedelta(days=1)
                tf_end = tf_start + timedelta(days=3) if tf_end is not None else None

            await self._update_directly(
                comp.id,
                registration_start=reg_start,
                registration_end=reg_end,
                is_archived=False,
                team_formation_start=tf_start,
                team_formation_end=tf_end,
            )

        return await self._read_many([c.id for c in competitions], organizer_auth_id)

    async def change_archived_state(
        self,
        competitions: list[CompetitionModel],
        organizer_auth_id: str,
        *,
        is_archived: bool,
    ) -> list[CompetitionModel]:
        """Set archived state for all competitions and return updated models."""
        for comp in competitions:
            await self._update_directly(comp.id, is_archived=is_archived)

        return await self._read_many([c.id for c in competitions], organizer_auth_id)

    async def activate(
        self,
        competition_id: CompetitionId,
        organizer_auth_id: str,
        *,
        tag_ids: list[CompetitionTagId],
        tracks: list[CompetitionTrackForm],
        auto_accept: bool = False,
        participant_type: ParticipantType = ParticipantType.ANY,
        max_participants: int = 10000,
    ) -> None:
        """Open registration window and update key competition fields.

        DB-updates ``registration_start`` into the past, then calls the API to set
        ``participant_type``, ``participant_limits``, ``is_archived``, ``tag_ids``, ``tracks``, ``auto_accept``.
        """
        competition_model = await self.read(competition_id, organizer_auth_id)
        await self.make_all_active([competition_model], organizer_auth_id)

        update_form = UpdateCompetitionForm(
            title=competition_model.title,
            description=competition_model.description,
            schedule=ScheduleData(
                registration_start=competition_model.schedule.registration_start,
                registration_end=competition_model.schedule.registration_end,
                team_formation_start=competition_model.schedule.team_formation_start,
                team_formation_end=competition_model.schedule.team_formation_end,
            ),
            venue=competition_model.venue,
            team_size=competition_model.team_size,
            milestones=[
                MilestoneForm(
                    title=m.title,
                    timestamp=m.timestamp,
                    description=m.description,
                )
                for m in competition_model.milestones
            ],
            participant_type=participant_type,
            participant_limits=ParticipantLimits(max=max_participants),
            is_archived=False,
            tag_ids=tag_ids,
            tracks=tracks,
            auto_accept=auto_accept,
        )
        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            (
                await self.api_client.update_competition(competition_id, update_form.model_dump(mode="json"))
            ).assert_status(200)

    # --- Creation ---

    async def create(self, organizer_auth_id: str, *, auto_accept: bool = True) -> CompetitionCreated:
        """Create a new competition as the given organizer."""
        form = self.competition_form_factory.build(auto_accept=auto_accept)

        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            created = (
                (await self.api_client.create_competition(form.model_dump(mode="json")))
                .assert_status(200)
                .ensure_content()
            )

        return CompetitionCreated(created=created, form=form)

    async def create_active(
        self,
        organizer_auth_id: str,
        *,
        auto_accept: bool = True,
        participant_type: ParticipantType = ParticipantType.ANY,
        max_participants: int = 10000,
        tag_ids: list[CompetitionTagId] | None = None,
    ) -> CompetitionCreated:
        """Create a new competition with open registration."""
        comp = await self.create(organizer_auth_id, auto_accept=auto_accept)

        await self.activate(
            comp.created.competition_id,
            organizer_auth_id,
            tag_ids=tag_ids if tag_ids is not None else comp.form.tag_ids,
            tracks=comp.form.tracks,
            auto_accept=auto_accept,
            participant_type=participant_type,
            max_participants=max_participants,
        )

        return comp

    async def create_unarchived(
        self,
        organizer_auth_id: str,
    ) -> CompetitionCreated:
        """Create a competition that is visible (unarchived) but whose registration hasn't started yet."""
        comp = await self.create(organizer_auth_id)
        update_form = self.update_competition_form_factory.build(
            participant_type=ParticipantType.ANY,
            is_archived=False,
            tag_ids=comp.form.tag_ids,
            tracks=comp.form.tracks,
            auto_accept=comp.form.auto_accept,
        )
        await self.update(comp.created.competition_id, update_form, organizer_auth_id)
        return comp

    async def create_from_form(self, organizer_auth_id: str, form: CompetitionForm) -> CompetitionModel:
        """Create a competition from an existing form and return the read model."""
        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            competition_id = (
                (await self.api_client.create_competition(form.model_dump(mode="json")))
                .assert_status(200)
                .ensure_content()
                .competition_id
            )
            return (await self.api_client.read_competition(competition_id)).assert_status(200).ensure_content()

    async def create_many(self, organizer_auth_id: str, n: int) -> list[CompetitionModel]:
        """Create N competitions in parallel and return their read models."""
        forms = [self.competition_form_factory.build() for _ in range(n)]
        return await self.create_many_from_form(organizer_auth_id, forms)

    async def create_many_from_form(
        self,
        organizer_auth_id: str,
        forms: list[CompetitionForm],
    ) -> list[CompetitionModel]:
        """Create competitions from the given forms in parallel and return their read models."""
        with self.api_client.authenticate(auth_user_id=organizer_auth_id):
            created_responses = await asyncio.gather(
                *[self.api_client.create_competition(form.model_dump(mode="json")) for form in forms],
            )
            created = [r.assert_status(200).ensure_content() for r in created_responses]

            read_responses = await asyncio.gather(
                *[self.api_client.read_competition(c.competition_id) for c in created],
            )

        return [r.assert_status(200).ensure_content() for r in read_responses]

    async def create_many_active(
        self,
        organizer_auth_id: str,
        n: int,
        *,
        participant_type: ParticipantType = ParticipantType.ANY,
    ) -> list[CompetitionModel]:
        """Create ``n`` competitions and open their registration so they're visible to explore.

        All rows are forced to ``participant_type`` (default ``ANY``) so explore eligibility
        filters don't silently drop them due to the factory's random participant_type.
        """
        competitions = await self.create_many(organizer_auth_id, n)
        for comp in competitions:
            await self._update_directly(comp.id, participant_type=participant_type)
        return await self.make_all_active(competitions, organizer_auth_id)

    async def create_many_mixed(self, organizer_auth_id: str, n: int) -> list[CompetitionModel]:
        """Create N competitions with mixed states (active, inactive, archived, passed).

        Distribution:
        - 40% active, 30% inactive, 20% passed, 10% archived
        """
        competitions = await self.create_many(organizer_auth_id, n)
        if not competitions:
            return []

        shuffled = competitions.copy()
        random.shuffle(shuffled)

        num_active = max(1, int(n * 0.4))
        num_inactive = max(1, int(n * 0.3))
        num_passed = max(1, int(n * 0.2))

        active_comps = shuffled[:num_active]
        inactive_comps = shuffled[num_active : num_active + num_inactive]
        passed_comps = shuffled[num_active + num_inactive : num_active + num_inactive + num_passed]
        archived_comps = shuffled[num_active + num_inactive + num_passed :]

        updated_active = await self.make_all_active(active_comps, organizer_auth_id)
        updated_passed = await self.make_all_passed(passed_comps, organizer_auth_id)
        updated_archived = await self.change_archived_state(archived_comps, organizer_auth_id, is_archived=True)

        return updated_active + inactive_comps + updated_passed + updated_archived
