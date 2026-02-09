from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class ParticipantContact:
    """Participant contact link with URL validation."""

    url: str

    def __post_init__(self) -> None:
        """Validate contact URL format."""
        parsed = urlparse(self.url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL")
