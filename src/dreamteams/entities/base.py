from abc import ABC
from dataclasses import dataclass


@dataclass
class Entity(ABC):  # noqa: B024
    """Base abstract class that all domain entities inherit from. Provides common structure for business objects."""
