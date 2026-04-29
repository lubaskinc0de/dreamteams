from typing import override

from argon2 import PasswordHasher as ArgonPasswordHasher
from argon2.exceptions import VerifyMismatchError
from opentelemetry import trace

from dreamteams.application.common.password_hasher import PasswordHasher

_tracer = trace.get_tracer("dreamteams.adapters")


class Argon2PasswordHasher(PasswordHasher):
    """Argon2-backed password hasher."""

    def __init__(self) -> None:
        self._ph = ArgonPasswordHasher()

    @override
    def verify(self, encoded_hash: str, password: str) -> bool:
        """Return True if *password* matches *encoded_hash*, False otherwise."""
        with _tracer.start_as_current_span("crypto.argon2_verify"):
            try:
                return self._ph.verify(encoded_hash, password)
            except VerifyMismatchError:
                return False
