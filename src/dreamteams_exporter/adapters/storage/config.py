from dataclasses import dataclass
from pathlib import Path
from typing import Self

import toml_rs
from adaptix import Retort

_retort = Retort()


@dataclass(slots=True, frozen=True, kw_only=True)
class S3Config:
    """S3-compatible object storage configuration for exported spreadsheets."""

    bucket_name: str
    endpoint_url: str
    access_key: str
    secret_key: str
    region: str
    public_url: str
    export_file_lifetime_days: int = 1

    @classmethod
    def from_toml(cls, path: str | Path) -> Self:
        """Loads the ``[s3]`` section of the given TOML file."""
        with Path(path).open("rb") as fh:
            data = toml_rs.load(fh)
        return _retort.load(data["s3"], cls)
