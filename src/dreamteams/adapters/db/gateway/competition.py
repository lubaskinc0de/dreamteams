# mypy: disable-error-code="empty-body"
from collections.abc import Callable
from datetime import UTC, datetime
from typing import override

import structlog
from adaptix.conversion import coercer, impl_converter
from opentelemetry import trace
from sqlalchemy import ColumnElement, Subquery, and_, asc, delete, desc, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dreamteams.adapters.db.models import (
    application_table,
    competition_table,
    competition_tag_link_table,
    competition_tag_table,
    competition_track_table,
    milestone_table,
    organizer_table,
    user_table,
)
from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.dto.competition import CompetitionModel
from dreamteams.application.common.dto.explore_competition import ExploreCompetitionModel, ExploreOrganizerModel
from dreamteams.application.common.dto.preview_competition import PreviewCompetitionModel, PreviewOrganizerModel
from dreamteams.application.common.gateway.competition import (
    CompetitionGateway,
    CompetitionSortBy,
    ExploreSortBy,
)
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.entities.application.entity import ApplicationStatus
from dreamteams.entities.common.identifiers import CompetitionId, CompetitionTagId, OrganizerId, ParticipantId
from dreamteams.entities.common.participant_type import ParticipantType
from dreamteams.entities.competition.entity import Competition
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.milestones import CompetitionMilestones
from dreamteams.entities.competition.tag import CompetitionTag
from dreamteams.entities.competition.tags import CompetitionTags
from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.entities.competition.tracks import CompetitionTracks
from dreamteams.entities.user import Organizer
from dreamteams_common.logger import Logger

_tracer = trace.get_tracer("dreamteams.adapters")

SIMILARITY_THRESHOLD = 0.15
logger: Logger = structlog.get_logger(__name__)


def _milestones_to_list(milestones: CompetitionMilestones) -> list[Milestone]:
    return list(milestones)


def _tags_to_list(tags: CompetitionTags) -> list[CompetitionTag]:
    return list(tags)


def _tracks_to_list(tracks: CompetitionTracks) -> list[CompetitionTrack]:
    return list(tracks)


@impl_converter(
    recipe=[
        coercer(CompetitionMilestones, list[Milestone], func=_milestones_to_list),
        coercer(CompetitionTags, list[CompetitionTag], func=_tags_to_list),
        coercer(CompetitionTracks, list[CompetitionTrack], func=_tracks_to_list),
    ],
)
def _to_competition_model(competition: Competition, members_count: int) -> CompetitionModel: ...


def _build_preview_converter(
    avatar_storage: AvatarStorage,
) -> Callable[[Competition, int], PreviewCompetitionModel]:
    """Build a Competition → PreviewCompetitionModel converter wired to this instance's avatar storage."""

    def organizer_to_preview(organizer: Organizer) -> PreviewOrganizerModel:
        avatar_key = organizer.user.avatar
        return PreviewOrganizerModel(
            id=organizer.id,
            name=organizer.organizer_name,
            avatar_url=avatar_storage.get_url(avatar_key) if avatar_key is not None else None,
        )

    @impl_converter(
        recipe=[
            coercer(Organizer, PreviewOrganizerModel, func=organizer_to_preview),
            coercer(CompetitionMilestones, list[Milestone], func=_milestones_to_list),
            coercer(CompetitionTags, list[CompetitionTag], func=_tags_to_list),
            coercer(CompetitionTracks, list[CompetitionTrack], func=_tracks_to_list),
        ],
    )
    def convert(competition: Competition, members_count: int) -> PreviewCompetitionModel: ...

    return convert


def _build_explore_converter(
    avatar_storage: AvatarStorage,
) -> Callable[[Competition, int], ExploreCompetitionModel]:
    """Build a Competition → ExploreCompetitionModel converter wired to this instance's avatar storage."""

    def organizer_to_explore(organizer: Organizer) -> ExploreOrganizerModel:
        avatar_key = organizer.user.avatar
        return ExploreOrganizerModel(
            id=organizer.id,
            name=organizer.organizer_name,
            avatar_url=avatar_storage.get_url(avatar_key) if avatar_key is not None else None,
        )

    @impl_converter(
        recipe=[
            coercer(Organizer, ExploreOrganizerModel, func=organizer_to_explore),
            coercer(CompetitionMilestones, list[Milestone], func=_milestones_to_list),
            coercer(CompetitionTags, list[CompetitionTag], func=_tags_to_list),
            coercer(CompetitionTracks, list[CompetitionTrack], func=_tracks_to_list),
        ],
    )
    def convert(competition: Competition, members_count: int) -> ExploreCompetitionModel: ...

    return convert


def _accepted_counts_subquery() -> Subquery:
    """
    Aggregated count of ACCEPTED applications grouped by competition.

    Used as a LEFT JOIN target so ``members_count`` is available in both SELECT and ORDER BY
    without re-evaluating a correlated subquery per candidate row.
    """
    return (
        select(
            application_table.c.competition_id.label("competition_id"),
            func.count().label("cnt"),
        )
        .where(application_table.c.status == ApplicationStatus.ACCEPTED)
        .group_by(application_table.c.competition_id)
        .subquery("accepted_counts")
    )


class SACompetitionGateway(CompetitionGateway):
    """SQLAlchemy-based implementation of CompetitionGateway."""

    def __init__(self, session: AsyncSession, avatar_storage: AvatarStorage) -> None:
        self._session = session
        self._to_preview = _build_preview_converter(avatar_storage)
        self._to_explore = _build_explore_converter(avatar_storage)

    @override
    async def get(
        self,
        competition_id: CompetitionId,
        *,
        eager_milestones: bool = False,
        eager_tags: bool = False,
        eager_tracks: bool = False,
        for_update: bool = False,
    ) -> Competition | None:
        """
        Fetch a competition by ID, optionally eager-loading relationships or locking the competition row.

        Returns None if the organizer's account is blocked.
        """
        query = (
            select(Competition)
            .join(organizer_table, organizer_table.c.id == competition_table.c.organizer_id)
            .join(user_table, user_table.c.id == organizer_table.c.user_id)
            .where(competition_table.c.id == competition_id, user_table.c.is_blocked.is_(False))
        )
        if eager_milestones:
            query = query.options(selectinload(Competition.milestones))  # type: ignore[arg-type]
        if eager_tags:
            query = query.options(selectinload(Competition.tags))  # type: ignore[arg-type]
        if eager_tracks:
            query = query.options(selectinload(Competition.tracks))  # type: ignore[arg-type]
        if for_update:
            query = query.with_for_update(of=competition_table)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    @override
    async def get_with_organizer(self, competition_id: CompetitionId) -> Competition | None:
        """
        Fetch a competition eager-loading organizer + organizer.user.

        Returns None if the organizer's account is blocked.
        """
        result = await self._session.execute(
            select(Competition)
            .join(organizer_table, organizer_table.c.id == competition_table.c.organizer_id)
            .join(user_table, user_table.c.id == organizer_table.c.user_id)
            .where(competition_table.c.id == competition_id, user_table.c.is_blocked.is_(False))
            .options(selectinload(Competition.organizer).selectinload(Organizer.user)),  # type: ignore[arg-type]
        )
        return result.scalar_one_or_none()

    @override
    async def clear_milestones(self, competition_id: CompetitionId) -> None:
        """Delete all milestones of a competition."""
        await self._session.execute(
            delete(Milestone).where(milestone_table.c.competition_id == competition_id),
        )

    @override
    async def clear_tracks(self, competition_id: CompetitionId) -> None:
        """Delete all tracks of a competition."""
        await self._session.execute(
            delete(CompetitionTrack).where(competition_track_table.c.competition_id == competition_id),
        )

    @override
    async def read(self, competition_id: CompetitionId) -> CompetitionModel | None:
        """Fetch a single competition as a CompetitionModel with members_count baked in."""
        accepted = _accepted_counts_subquery()
        members_count = func.coalesce(accepted.c.cnt, 0)
        query = (
            select(Competition, members_count.label("members_count"))
            .outerjoin(accepted, accepted.c.competition_id == competition_table.c.id)
            .join(organizer_table, organizer_table.c.id == competition_table.c.organizer_id)
            .join(user_table, user_table.c.id == organizer_table.c.user_id)
            .where(competition_table.c.id == competition_id, user_table.c.is_blocked.is_(False))
            .options(
                selectinload(Competition.milestones),  # type: ignore[arg-type]
                selectinload(Competition.tags),  # type: ignore[arg-type]
                selectinload(Competition.tracks),  # type: ignore[arg-type]
            )
        )
        row = (await self._session.execute(query)).one_or_none()
        if row is None:
            return None
        return _to_competition_model(row[0], row.members_count)

    @override
    async def list_for_organizer(
        self,
        organizer_id: OrganizerId,
        *,
        page: int,
        page_size: int,
        sort_by: CompetitionSortBy,
        sort_order: SortOrder,
        is_archived: bool | None,
        search: str | None,
    ) -> tuple[list[CompetitionModel], int]:
        """Organizer's own competitions with pagination, sorting and filters; members_count baked in."""
        sort_column = {
            CompetitionSortBy.CREATED_AT: competition_table.c.created_at,
            CompetitionSortBy.TITLE: competition_table.c.title,
            CompetitionSortBy.REGISTRATION_START: competition_table.c.registration_start,
            CompetitionSortBy.TEAM_FORMATION_START: competition_table.c.team_formation_start,
        }[sort_by]
        direction = desc if sort_order == SortOrder.DESC else asc
        order_by: list[ColumnElement[object]] = [direction(sort_column)]

        filters: list[ColumnElement[bool]] = [competition_table.c.organizer_id == organizer_id]
        if is_archived is not None:
            filters.append(competition_table.c.is_archived == is_archived)

        if search is not None:
            similarity = func.word_similarity(func.lower(competition_table.c.title), search.lower())
            filters.append(similarity > SIMILARITY_THRESHOLD)
            order_by.insert(0, similarity.desc())

        order_by.append(direction(competition_table.c.id))

        with _tracer.start_as_current_span("db.competition_list_for_organizer"):
            accepted = _accepted_counts_subquery()
            members_count = func.coalesce(accepted.c.cnt, 0)
            total_col = func.count().over().label("total")
            query = (
                select(Competition, members_count.label("members_count"), total_col)
                .outerjoin(accepted, accepted.c.competition_id == competition_table.c.id)
                .where(*filters)
                .order_by(*order_by)
                .limit(page_size)
                .offset((page - 1) * page_size)
                .options(
                    selectinload(Competition.milestones),  # type: ignore[arg-type]
                    selectinload(Competition.tags),  # type: ignore[arg-type]
                    selectinload(Competition.tracks),  # type: ignore[arg-type]
                )
            )
            result = (await self._session.execute(query)).all()
            rows = [_to_competition_model(row[0], row.members_count) for row in result]
            total = result[0].total if result else 0
            return rows, total

    @override
    async def list_preview(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[PreviewCompetitionModel], int]:
        """Anonymous preview: non-archived, active-registration competitions with members_count."""
        now = datetime.now(tz=UTC)
        filters: list[ColumnElement[bool]] = [
            competition_table.c.is_archived.is_(False),
            competition_table.c.registration_start < now,
            competition_table.c.registration_end > now,
        ]

        with _tracer.start_as_current_span("db.competition_list_preview"):
            accepted = _accepted_counts_subquery()
            members_count = func.coalesce(accepted.c.cnt, 0)
            total_col = func.count().over().label("total")
            query = (
                select(Competition, members_count.label("members_count"), total_col)
                .outerjoin(accepted, accepted.c.competition_id == competition_table.c.id)
                .join(organizer_table, organizer_table.c.id == competition_table.c.organizer_id)
                .join(user_table, user_table.c.id == organizer_table.c.user_id)
                .where(*filters, user_table.c.is_blocked.is_(False))
                .order_by(desc(competition_table.c.created_at), desc(competition_table.c.id))
                .limit(page_size)
                .offset((page - 1) * page_size)
                .options(
                    selectinload(Competition.organizer).selectinload(Organizer.user),  # type: ignore[arg-type]
                    selectinload(Competition.milestones),  # type: ignore[arg-type]
                    selectinload(Competition.tags),  # type: ignore[arg-type]
                    selectinload(Competition.tracks),  # type: ignore[arg-type]
                )
            )
            result = (await self._session.execute(query)).all()
            rows = [self._to_preview(row[0], row.members_count) for row in result]
            total = result[0].total if result else 0
            return rows, total

    @override
    async def explore(
        self,
        *,
        participant_id: ParticipantId,
        participant_type: ParticipantType,
        page: int,
        page_size: int,
        sort_by: ExploreSortBy,
        search: str | None,
        min_team_size: int | None,
        max_team_size: int | None,
        auto_accept: bool | None,
        tag_ids: list[CompetitionTagId] | None,
    ) -> tuple[list[ExploreCompetitionModel], int]:
        """Participant-facing browse: only competitions the participant can still submit to."""
        now = datetime.now(tz=UTC)
        accepted = _accepted_counts_subquery()
        members_count = func.coalesce(accepted.c.cnt, 0)

        already_applied = exists().where(
            and_(
                application_table.c.competition_id == competition_table.c.id,
                application_table.c.participant_id == participant_id,
            ),
        )

        filters: list[ColumnElement[bool]] = [
            competition_table.c.is_archived.is_(False),
            competition_table.c.registration_start < now,
            competition_table.c.registration_end > now,
            ~already_applied,
            or_(
                competition_table.c.participant_type == ParticipantType.ANY,
                competition_table.c.participant_type == participant_type,
            ),
            members_count < competition_table.c.max_participants,
        ]

        if min_team_size is not None:
            filters.append(competition_table.c.max_team_size >= min_team_size)
        if max_team_size is not None:
            filters.append(competition_table.c.min_team_size <= max_team_size)
        if auto_accept is not None:
            filters.append(competition_table.c.auto_accept == auto_accept)
        if tag_ids:
            has_requested_tag = exists().where(
                and_(
                    competition_tag_link_table.c.competition_id == competition_table.c.id,
                    competition_tag_link_table.c.tag_id.in_(tag_ids),
                ),
            )
            filters.append(has_requested_tag)

        order_by: list[ColumnElement[object]] = []
        if search is not None:
            search_value = search.lower()
            title_similarity = func.word_similarity(func.lower(competition_table.c.title), search_value)
            tag_similarity = (
                select(func.max(func.word_similarity(func.lower(competition_tag_table.c.value), search_value)))
                .select_from(
                    competition_tag_link_table.join(
                        competition_tag_table,
                        competition_tag_table.c.id == competition_tag_link_table.c.tag_id,
                    ),
                )
                .where(competition_tag_link_table.c.competition_id == competition_table.c.id)
                .scalar_subquery()
            )
            similarity = func.greatest(title_similarity, func.coalesce(tag_similarity, 0))
            filters.append(similarity > SIMILARITY_THRESHOLD)
            order_by.append(similarity.desc())

        if sort_by == ExploreSortBy.MOST_POPULAR:
            order_by.extend([members_count.desc(), desc(competition_table.c.created_at)])
        else:
            order_by.append(desc(competition_table.c.created_at))
        order_by.append(desc(competition_table.c.id))

        with _tracer.start_as_current_span("db.competition_explore"):
            total_col = func.count().over().label("total")
            query = (
                select(Competition, members_count.label("members_count"), total_col)
                .outerjoin(accepted, accepted.c.competition_id == competition_table.c.id)
                .join(organizer_table, organizer_table.c.id == competition_table.c.organizer_id)
                .join(user_table, user_table.c.id == organizer_table.c.user_id)
                .where(*filters, user_table.c.is_blocked.is_(False))
                .order_by(*order_by)
                .limit(page_size)
                .offset((page - 1) * page_size)
                .options(
                    selectinload(Competition.organizer).selectinload(Organizer.user),  # type: ignore[arg-type]
                    selectinload(Competition.milestones),  # type: ignore[arg-type]
                    selectinload(Competition.tags),  # type: ignore[arg-type]
                    selectinload(Competition.tracks),  # type: ignore[arg-type]
                )
            )
            result = (await self._session.execute(query)).all()
            rows = [self._to_explore(row[0], row.members_count) for row in result]
            total = result[0].total if result else 0
            return rows, total
