from collections.abc import Callable
from datetime import datetime

from dreamteams.application.common.dto.explore_competition import ExploreCompetitionModel, ExploreOrganizerModel
from dreamteams.application.common.dto.preview_competition import PreviewCompetitionModel, PreviewOrganizerModel
from dreamteams.application.common.gateway.competition import CompetitionSortBy
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.application.delete_my_competition import CompetitionModel
from dreamteams.application.preview_competitions.preview_competitions import PreviewCompetitionsList
from dreamteams.application.publish_competition.publish_competition import CompetitionForm
from dreamteams.application.submit_application.list_competitions import ExploreCompetitionsList
from dreamteams.application.update_my_competition import (
    RescheduleCompetitionForm,
    UpdateCompetitionGeneralInfoForm,
)
from dreamteams.application.view_my_competitions.list_competitions import PAGE_SIZE, CompetitionsList
from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId
from dreamteams.entities.competition.milestone import Milestone
from dreamteams.entities.competition.schedule import schedule_factory
from dreamteams.entities.competition.tag import CompetitionTag
from dreamteams.entities.competition.track import CompetitionTrack
from dreamteams.presentation.fast_api.routers.organizers import OrganizerForm


def create_competitions_list(
    competitions: list[CompetitionModel],
    sort_by: CompetitionSortBy | None,
    sort_order: SortOrder | None,
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> CompetitionsList:
    """Create ``CompetitionsList`` from ``list[CompetitionModel]`` with sorting and pagination applied."""
    sort_key_mapping: dict[CompetitionSortBy, Callable[[CompetitionModel], tuple[datetime | str, CompetitionId]]] = {
        CompetitionSortBy.CREATED_AT: lambda c: (c.created_at, c.id),
        CompetitionSortBy.TITLE: lambda c: (c.title, c.id),
        CompetitionSortBy.REGISTRATION_START: lambda c: (c.schedule.registration_start, c.id),
    }

    sorted_items = (
        sorted(
            competitions,
            key=sort_key_mapping[sort_by],
            reverse=(sort_order == SortOrder.DESC),
        )
        if sort_by is not None and sort_order is not None
        else competitions
    )

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = sorted_items[start_idx:end_idx]

    return CompetitionsList(
        items=paginated_items,
        total=len(competitions),
        page=page,
    )


def competition_form_to_model(
    competition_id: CompetitionId,
    organizer_id: OrganizerId,
    created_at: datetime,
    updated_at: datetime,
    form: CompetitionForm,
    clock: Clock,
    *,
    members_count: int = 0,
    tags: list[CompetitionTag] | None = None,
) -> CompetitionModel:
    """Transform competition form and additional data to CompetitionModel."""
    return CompetitionModel(
        id=competition_id,
        organizer_id=organizer_id,
        title=form.title,
        banner=None,
        description=form.description,
        schedule=schedule_factory(form.schedule, clock),
        participant_limits=form.participant_limits,
        tags=sorted(tags or [], key=lambda tag: tag.value),
        tracks=[CompetitionTrack(track.name) for track in sorted(form.tracks, key=lambda item: item.name)],
        participant_type=form.participant_type,
        venue=form.venue,
        team_size=form.team_size,
        milestones=[
            Milestone(
                timestamp=milestone.timestamp,
                title=milestone.title,
                description=milestone.description,
            )
            for milestone in sorted(form.milestones, key=lambda item: item.timestamp)
        ],
        auto_accept=form.auto_accept,
        is_archived=True,
        members_count=members_count,
        created_at=created_at,
        updated_at=updated_at,
    )


def competition_general_info_form_to_model(
    competition_id: CompetitionId,
    organizer_id: OrganizerId,
    created_at: datetime,
    updated_at: datetime,
    current: CompetitionModel,
    form: UpdateCompetitionGeneralInfoForm,
    *,
    members_count: int = 0,
    tags: list[CompetitionTag] | None = None,
) -> CompetitionModel:
    """Transform competition general-info update form and existing data to CompetitionModel."""
    return CompetitionModel(
        id=competition_id,
        organizer_id=organizer_id,
        title=form.title,
        banner=current.banner,
        description=form.description,
        schedule=current.schedule,
        participant_limits=form.participant_limits,
        tags=sorted(tags or [], key=lambda tag: tag.value),
        tracks=[CompetitionTrack(track.name) for track in sorted(form.tracks, key=lambda item: item.name)],
        participant_type=form.participant_type,
        venue=form.venue,
        team_size=current.team_size,
        milestones=[
            Milestone(
                timestamp=milestone.timestamp,
                title=milestone.title,
                description=milestone.description,
            )
            for milestone in sorted(form.milestones or [], key=lambda item: item.timestamp)
        ],
        auto_accept=form.auto_accept,
        is_archived=current.is_archived,
        members_count=members_count,
        created_at=created_at,
        updated_at=updated_at,
    )


def competition_reschedule_form_to_model(
    current: CompetitionModel,
    form: RescheduleCompetitionForm,
    updated_at: datetime,
    clock: Clock,
) -> CompetitionModel:
    """Transform competition reschedule form and existing data to CompetitionModel."""
    return CompetitionModel(
        id=current.id,
        organizer_id=current.organizer_id,
        title=current.title,
        banner=current.banner,
        description=current.description,
        schedule=schedule_factory(form.schedule, clock),
        participant_limits=current.participant_limits,
        tags=current.tags,
        tracks=current.tracks,
        participant_type=current.participant_type,
        venue=current.venue,
        team_size=form.team_size,
        milestones=current.milestones,
        auto_accept=current.auto_accept,
        is_archived=current.is_archived,
        members_count=current.members_count,
        created_at=current.created_at,
        updated_at=updated_at,
    )


def competitions_list_to_preview_list(
    lst: CompetitionsList,
    organizer_form: OrganizerForm,
    organizer_id: OrganizerId,
) -> PreviewCompetitionsList:
    """Transform CompetitionsList to PreviewCompetitionsList with organizer info."""
    organizer_model = PreviewOrganizerModel(
        id=organizer_id,
        name=organizer_form.organizer_name,
        avatar_url=None,
    )

    preview_items = [
        PreviewCompetitionModel(
            id=comp.id,
            organizer=organizer_model,
            title=comp.title,
            banner=comp.banner,
            description=comp.description,
            schedule=comp.schedule,
            participant_limits=comp.participant_limits,
            tags=comp.tags,
            tracks=comp.tracks,
            participant_type=comp.participant_type,
            venue=comp.venue,
            team_size=comp.team_size,
            milestones=comp.milestones,
            auto_accept=comp.auto_accept,
            is_archived=comp.is_archived,
            members_count=comp.members_count,
            created_at=comp.created_at,
            updated_at=comp.updated_at,
        )
        for comp in lst.items
    ]

    return PreviewCompetitionsList(total=lst.total, page=lst.page, items=preview_items)


def competitions_list_to_explore_list(
    lst: CompetitionsList,
    organizer_form: OrganizerForm,
    organizer_id: OrganizerId,
) -> ExploreCompetitionsList:
    """Transform CompetitionsList to ExploreCompetitionsList with organizer info populated."""
    organizer_model = ExploreOrganizerModel(
        id=organizer_id,
        name=organizer_form.organizer_name,
        avatar_url=None,
    )

    explore_items = [
        ExploreCompetitionModel(
            id=comp.id,
            organizer=organizer_model,
            title=comp.title,
            banner=comp.banner,
            description=comp.description,
            schedule=comp.schedule,
            participant_limits=comp.participant_limits,
            tags=comp.tags,
            tracks=comp.tracks,
            participant_type=comp.participant_type,
            venue=comp.venue,
            team_size=comp.team_size,
            milestones=comp.milestones,
            auto_accept=comp.auto_accept,
            members_count=comp.members_count,
            created_at=comp.created_at,
            updated_at=comp.updated_at,
        )
        for comp in lst.items
    ]

    return ExploreCompetitionsList(total=lst.total, page=lst.page, items=explore_items)
