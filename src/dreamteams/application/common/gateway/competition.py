from abc import abstractmethod
from enum import StrEnum, auto
from typing import Protocol

from dreamteams.application.common.dto.competition import CompetitionModel
from dreamteams.application.common.dto.explore_competition import ExploreCompetitionModel
from dreamteams.application.common.dto.preview_competition import PreviewCompetitionModel
from dreamteams.application.common.gateway.sorting import SortOrder
from dreamteams.entities.common.identifiers import CompetitionId, OrganizerId, ParticipantId
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import Competition


class CompetitionSortBy(StrEnum):
    """Fields available for sorting competitions."""

    CREATED_AT = auto()
    TITLE = auto()
    REGISTRATION_START = auto()
    TEAM_FORMATION_START = auto()


class ExploreSortBy(StrEnum):
    """Fields available for sorting competitions when exploring as a participant."""

    MOST_POPULAR = auto()
    NEWEST = auto()


class CompetitionGateway(Protocol):
    """Protocol defining the interface for reading competition data from persistent storage."""

    @abstractmethod
    async def get(
        self,
        competition_id: CompetitionId,
        *,
        eager_milestones: bool = False,
    ) -> Competition | None:
        """Retrieves a competition entity by its unique identifier, returns None if not found.

        Set ``eager_milestones=True`` when the caller renders milestones in its response —
        otherwise the relationship raises on access.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_with_organizer(self, competition_id: CompetitionId) -> Competition | None:
        """Retrieves a competition with the organizer (and organizer.user) eagerly loaded."""
        raise NotImplementedError

    @abstractmethod
    async def clear_milestones(self, competition_id: CompetitionId) -> None:
        """Delete all competition milestones from storage."""
        raise NotImplementedError

    @abstractmethod
    async def read(self, competition_id: CompetitionId) -> CompetitionModel | None:
        """Fetch a single competition as a manage-competitions read model (with ``members_count``)."""
        raise NotImplementedError

    @abstractmethod
    async def list_for_organizer(  # noqa: PLR0913
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
        """List an organizer's own competitions with pagination, sorting and filters.

        Each row's ``members_count`` (number of ACCEPTED applications) is computed in the
        same SQL query.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_preview(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[PreviewCompetitionModel], int]:
        """Anonymous preview list: non-archived competitions in an active registration window.

        Each row's ``members_count`` is computed in the same SQL query.
        """
        raise NotImplementedError

    @abstractmethod
    async def explore(  # noqa: PLR0913
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
        domains: list[Domain] | None,
    ) -> tuple[list[ExploreCompetitionModel], int]:
        """Participant-facing browse: only competitions the participant can still submit to.

        Eligibility filters (always applied):
        - non-archived and inside active registration window
        - participant has not already submitted an application to the competition
        - competition's ``participant_type`` is ``ANY`` or matches the participant's type
        - accepted applications (``members_count``) are below ``participant_limits.max``

        Additional optional filters:
        - ``min_team_size`` / ``max_team_size``: the competition's own team-size range must
          overlap with [min, max]
        - ``auto_accept``: exact match when provided
        - ``domains``: competition's domains must overlap with any of the provided
        - ``search``: trigram similarity on the title

        ``MOST_POPULAR`` sorts by ``members_count`` desc; ``NEWEST`` sorts by ``created_at`` desc.
        """
        raise NotImplementedError
