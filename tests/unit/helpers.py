from datetime import datetime
from zoneinfo import ZoneInfo

from hypothesis import strategies as st


@st.composite
def ordered_pairs(draw: st.DrawFn) -> tuple[int, int]:
    """Ordered pairs of positive integers."""
    n1 = draw(st.integers())
    n2 = draw(st.integers(min_value=n1))
    return (n1, n2)


@st.composite
def dt_past(draw: st.DrawFn) -> datetime:
    """Datetime in past."""
    return draw(
        st.datetimes(
            max_value=datetime.now(),  # noqa: DTZ005
            timezones=st.just(ZoneInfo("UTC")),
        ),
    )


@st.composite
def dt_future(draw: st.DrawFn) -> datetime:
    """Datetime in future."""
    return draw(
        st.datetimes(
            min_value=datetime.now(),  # noqa: DTZ005
            timezones=st.just(ZoneInfo("UTC")),
        ),
    )
