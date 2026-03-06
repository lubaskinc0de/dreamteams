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
from dreamteams.entities.participant.entity import (
    ExperienceLevel,
    ParticipantData,
)
from dreamteams.entities.participant.vo.participant_contact import ParticipantContact
from dreamteams.entities.participant.vo.participant_skill import ParticipantSkill, SkillLevel
from dreamteams.entities.user import User
from tests.unit.conftest import NOW_NAIVE


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
    base_date = draw(dt_past(max_dt=NOW_NAIVE - timedelta(minutes=4)))

    return CompetitionSchedule(
        registration_start=base_date,
        registration_end=base_date + timedelta(minutes=1),
        team_formation_start=base_date + timedelta(minutes=2),
        team_formation_end=base_date + timedelta(minutes=3),
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


@st.composite
def domain_data(draw: st.DrawFn) -> Domain:
    """Random Domain enum value."""
    return draw(st.sampled_from(list(Domain)))


@st.composite
def url_data(draw: st.DrawFn) -> str:
    """Random valid url."""
    scheme = draw(st.sampled_from(["https", "http"]))
    host = draw(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz0123456789-",
            min_size=3,
            max_size=15,
        ),
    )
    tld = draw(st.sampled_from(["com", "net", "org", "io", "ru"]))
    path = draw(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_/",
            min_size=0,
            max_size=20,
        ),
    )
    return f"{scheme}://{host}.{tld}/{path}"


@st.composite
def participant_skill_data(draw: st.DrawFn) -> ParticipantSkill:
    """Valid ParticipantSkill."""
    return ParticipantSkill(
        name=draw(valid_text()),
        level=draw(st.sampled_from(list(SkillLevel))),
    )


@st.composite
def participant_contact_data(draw: st.DrawFn) -> ParticipantContact:
    """Valid ParticipantContact."""
    return ParticipantContact(
        title=draw(valid_text()),
        url=draw(url_data()),
    )


@st.composite
def valid_participant_data(draw: st.DrawFn) -> ParticipantData:
    """Valid participant data."""
    full_name = draw(valid_text())
    bio = draw(valid_text())

    skills = draw(st.lists(participant_skill_data(), min_size=1, max_size=5))

    experience_level = draw(st.sampled_from(list(ExperienceLevel)))

    preferred_domains = draw(st.lists(domain_data(), min_size=1, max_size=5))

    contacts = draw(st.lists(participant_contact_data(), min_size=1, max_size=5))
    contacts_unique = {c.url: c for c in contacts}.values()

    return ParticipantData(
        full_name=full_name,
        avatar_url=None,
        bio=bio,
        skills=skills,
        experience_level=experience_level,
        preferred_domains=preferred_domains,
        contacts=contacts_unique,
    )
