from datetime import datetime


def normalize_datetime(dt: datetime) -> datetime:
    """Normalize datetime by removing seconds and microseconds."""
    return dt.replace(second=0, microsecond=0)
