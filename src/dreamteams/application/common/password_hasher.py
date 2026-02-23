from abc import abstractmethod
from typing import Protocol


class PasswordHasher(Protocol):
    """Protocol for verifying passwords against stored hashes."""

    @abstractmethod
    def verify(self, encoded_hash: str, password: str) -> bool:
        """Return True if *password* matches *encoded_hash*, False otherwise."""
        raise NotImplementedError
