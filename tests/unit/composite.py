from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from hypothesis import strategies as st

from dreamteams.entities.common.clock import Clock
from dreamteams.entities.common.vo.domain import Domain
from dreamteams.entities.common.vo.participant_type import ParticipantType
from dreamteams.entities.competition.entity import (
    Competition,
    CompetitionData,
    UpdateCompetitionData,
    competition_factory,
)
from dreamteams.entities.competition.milestone import Milestone, MilestoneData
from dreamteams.entities.competition.participant_limits import ParticipantLimits
from dreamteams.entities.competition.schedule import CompetitionSchedule, ScheduleData
from dreamteams.entities.competition.team_size_range import TeamSizeRange
from dreamteams.entities.competition.venue import CompetitionFormat, CompetitionVenue
from dreamteams.entities.user import User
from tests.unit.entities.competition.conftest import NOW_NAIVE


@st.composite
def ordered_pairs(draw: st.DrawFn) -> tuple[int, int]:
    """Ordered pairs (min, max) of integers."""
    n1 = draw(st.integers())
    n2 = draw(st.integers(min_value=n1))
    return (n1, n2)


@st.composite
def dt_past(draw: st.DrawFn, min_dt: datetime | None = None, max_dt: datetime | None = None) -> datetime:
    """Datetime in past."""
    max_value = min(max_dt, NOW_NAIVE - timedelta(minutes=1)) if max_dt else NOW_NAIVE - timedelta(minutes=1)

    if min_dt is None:
        return draw(
            st.datetimes(
                max_value=max_value,
                timezones=st.just(ZoneInfo("UTC")),
            ),
        )
    return draw(
        st.datetimes(
            min_value=min_dt,
            max_value=max_value,
            timezones=st.just(ZoneInfo("UTC")),
        ),
    )


@st.composite
def dt_future(draw: st.DrawFn, min_dt: datetime | None = None) -> datetime:
    """Datetime in future."""
    if min_dt is not None:
        assert min_dt > NOW_NAIVE
    min_v = min_dt or NOW_NAIVE + timedelta(minutes=1)
    return draw(
        st.datetimes(
            min_value=min_v,
            max_value=min_v + timedelta(days=365 * 5),
            timezones=st.just(ZoneInfo("UTC")),
        ),
    )


@st.composite
def valid_schedule_data(draw: st.DrawFn, min_dt: datetime | None = None) -> ScheduleData:
    """Valid schedule data with team formation period."""
    r_start = draw(dt_future(min_dt=min_dt))
    r_end = draw(dt_future(r_start.replace(tzinfo=None) + timedelta(minutes=1)))
    tf_start = draw(dt_future(r_end.replace(tzinfo=None) + timedelta(minutes=1)))
    tf_end = draw(dt_future(tf_start.replace(tzinfo=None) + timedelta(minutes=1)))
    return ScheduleData(
        registration_start=r_start,
        registration_end=r_end,
        team_formation_start=tf_start,
        team_formation_end=tf_end,
    )


@st.composite
def past_schedule(draw: st.DrawFn) -> CompetitionSchedule:
    """CompetitionSchedule with team formation period with dates in past."""
    tf_end = draw(dt_past())
    tf_start = draw(dt_past(max_dt=tf_end.replace(tzinfo=None) - timedelta(minutes=1)))
    r_end = draw(dt_past(max_dt=tf_start.replace(tzinfo=None) - timedelta(minutes=1)))
    r_start = draw(dt_past(max_dt=r_end.replace(tzinfo=None) - timedelta(minutes=1)))

    return CompetitionSchedule(
        registration_start=r_start,
        registration_end=r_end,
        team_formation_start=tf_start,
        team_formation_end=tf_end,
    )


@st.composite
def valid_text(draw: st.DrawFn) -> str:
    """Valid text with min_length = 1, contains only non-space characters."""
    return draw(st.text(st.characters().filter(lambda c: c and not c.isspace()), min_size=1))


@st.composite
def milestone_data(draw: st.DrawFn) -> MilestoneData:
    """Valid milestone data."""
    return MilestoneData(
        title=draw(valid_text()),
        timestamp=draw(dt_future()),
    )


@st.composite
def milestone(draw: st.DrawFn) -> Milestone:
    """Valid milestone."""
    return Milestone(
        title=draw(valid_text()),
        timestamp=draw(dt_future()),
    )


@st.composite
def valid_competition_data(draw: st.DrawFn) -> CompetitionData:
    """Valid competition data."""
    min_participants, max_participants = draw(ordered_pairs().filter(lambda pair: pair[0] > 0 and pair[1] > 0))
    min_team, max_team = draw(ordered_pairs().filter(lambda pair: pair[0] > 0 and pair[1] > 0))
    venue_format = draw(st.sampled_from(CompetitionFormat))
    return CompetitionData(
        title=draw(valid_text()),
        description=draw(valid_text()),
        schedule=draw(valid_schedule_data()),
        participant_limits=ParticipantLimits(
            max=max_participants,
            min=min_participants,
        ),
        domains=draw(st.lists(st.sampled_from(Domain), min_size=1)),
        venue=CompetitionVenue(
            format=venue_format,
            location=draw(valid_text())
            if venue_format in [CompetitionFormat.OFFLINE, CompetitionFormat.HYBRID]
            else None,
        ),
        team_size=TeamSizeRange(min=min_team, max=max_team),
        participant_type=draw(st.sampled_from(ParticipantType)),
        milestones=draw(
            st.one_of(st.none(), st.lists(milestone_data(), unique_by=lambda milestone: milestone.timestamp)),
        ),
    )


@st.composite
def valid_competition(draw: st.DrawFn, user: User, clock: Clock) -> Competition:
    """Valid competition entity."""
    data = draw(valid_competition_data())
    return competition_factory(data, user, clock)


@st.composite
def valid_competition_update_data(draw: st.DrawFn) -> UpdateCompetitionData:
    """Valid competition update data."""
    min_participants, max_participants = draw(ordered_pairs().filter(lambda pair: pair[0] > 0 and pair[1] > 0))
    min_team, max_team = draw(ordered_pairs().filter(lambda pair: pair[0] > 0 and pair[1] > 0))
    venue_format = draw(st.sampled_from(CompetitionFormat))
    return UpdateCompetitionData(
        title=draw(valid_text()),
        description=draw(valid_text()),
        schedule=draw(valid_schedule_data()),
        participant_limits=ParticipantLimits(
            max=max_participants,
            min=min_participants,
        ),
        domains=draw(st.lists(st.sampled_from(Domain), min_size=1)),
        venue=CompetitionVenue(
            format=venue_format,
            location=draw(valid_text())
            if venue_format in [CompetitionFormat.OFFLINE, CompetitionFormat.HYBRID]
            else None,
        ),
        team_size=TeamSizeRange(min=min_team, max=max_team),
        participant_type=draw(st.sampled_from(ParticipantType)),
        milestones=draw(
            st.one_of(
                st.none(),
                st.lists(
                    milestone(),
                    unique_by=lambda milestone: milestone.timestamp,
                ),
            ),
        ),
        is_archived=draw(st.booleans()),
    )
