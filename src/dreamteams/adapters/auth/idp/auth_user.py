from dataclasses import dataclass
from typing import Any, override

import jwt
import structlog
from fastapi import Request
from opentelemetry import trace

from dreamteams.adapters.auth.errors.base import UnauthorizedError, UnauthorizedReason
from dreamteams.adapters.auth.idp.base import AuthUserIdProvider
from dreamteams.adapters.auth.model import AuthUserId
from dreamteams.application.common.logger import Logger

_tracer = trace.get_tracer("dreamteams.adapters")

logger: Logger = structlog.get_logger(__name__)


@dataclass(slots=True, frozen=True, kw_only=True)
class WebAuthUserIdProviderConfig:
    """Configuration for web-based authentication user ID provider."""

    user_id_header: str
    user_email_header: str
    access_token_header: str
    access_token_alg: str
    allow_unverified_email: bool


class WebAuthUserIdProvider(AuthUserIdProvider):
    """Adapter that extracts authentication user ID from HTTP request headers."""

    def __init__(self, http_request: Request, config: WebAuthUserIdProviderConfig) -> None:
        self._http_request = http_request
        self._config = config

    def get_auth_user_email(self) -> str:
        """Reads the auth user email from the configured HTTP header."""
        user_email = self._http_request.headers.get(self._config.user_email_header)
        if user_email is None:
            msg = f"Missing {self._config.user_email_header} header"
            raise UnauthorizedError(
                message=msg,
                reason=UnauthorizedReason.MISSING_USER_EMAIL,
                header=self._config.user_email_header,
            )
        return user_email

    @override
    async def get_auth_user_id(self) -> AuthUserId:
        """Reads the auth user ID from the configured HTTP header, raises UnauthorizedError if header is missing."""
        with _tracer.start_as_current_span("auth.verify_token"):
            if (user_id := self._http_request.headers.get(self._config.user_id_header)) is None:
                logger.debug("Request unauthorized due to missing user id header", header=self._config.user_id_header)
                msg = f"Missing {self._config.user_id_header} header"
                raise UnauthorizedError(
                    message=msg,
                    reason=UnauthorizedReason.MISSING_USER_ID,
                    header=self._config.user_id_header,
                )

            if not self._config.allow_unverified_email:
                self._ensure_email_verified()
            return user_id

    def _get_access_token_data(self) -> dict[str, Any]:
        access_token = self._http_request.headers.get(self._config.access_token_header)
        if access_token is None:
            logger.debug(
                "Request unauthorized due to missing access token header",
                header=self._config.access_token_header,
            )
            msg = f"Missing {self._config.access_token_header} header"
            raise UnauthorizedError(
                message=msg,
                reason=UnauthorizedReason.MISSING_ACCESS_TOKEN,
                header=self._config.access_token_header,
            )
        return jwt.decode(  # type: ignore[no-any-return]
            access_token,
            options={"verify_signature": False, "verify_exp": True},
            algorithms=[self._config.access_token_alg],
        )

    def _ensure_email_verified(self) -> None:
        try:
            email_verified: bool = self._get_access_token_data()["email_verified"]
        except KeyError as e:
            logger.debug("Request unauthorized due to corrupted access token")
            raise UnauthorizedError(
                message="Corrupted access token",
                reason=UnauthorizedReason.CORRUPTED_ACCESS_TOKEN,
            ) from e

        logger.debug("Email verified status", status=email_verified)
        if not email_verified:
            raise UnauthorizedError(
                message="Email is not verified",
                reason=UnauthorizedReason.EMAIL_IS_NOT_VERIFIED,
            )
