from collections.abc import Iterator
from importlib.resources import as_file, files
from pathlib import Path

import dreamteams_exporter.adapters.db.alembic


def get_alembic_config_path() -> Iterator[Path]:
    """Yields the on-disk path to the exporter's alembic.ini as an ``importlib.resources`` context."""
    source = files(dreamteams_exporter.adapters.db.alembic).joinpath("alembic.ini")
    with as_file(source) as path:
        yield path
