import json
from abc import ABC
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, BinaryIO, override
from urllib.parse import quote

import aioboto3
import structlog
from botocore.exceptions import ClientError

from dreamteams.application.common.avatar_storage import AvatarStorage
from dreamteams.application.common.logger import Logger
from dreamteams.entities.common.identifiers import UserId

logger: Logger = structlog.get_logger(__name__)


@dataclass(slots=True, frozen=True)
class S3Config:
    """Config for S3 client."""

    bucket_name: str
    endpoint_url: str
    access_key: str
    secret_key: str
    region: str
    public_url: str


class S3Client(ABC):  # noqa: B024
    """Base S3 client."""

    def __init__(
        self,
        config: S3Config,
    ) -> None:
        self.bucket = config.bucket_name
        self.endpoint = config.endpoint_url
        self.region = config.region
        self.public_url = config.public_url

        self.session = aioboto3.Session(
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        )

    @asynccontextmanager
    async def _get_s3_client(self) -> AsyncGenerator[Any]:
        """Async context manager for S3 client."""
        async with self.session.client(
            service_name="s3",
            endpoint_url=self.endpoint,
            region_name=self.region,
        ) as s3_client:
            yield s3_client

    async def ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            async with self._get_s3_client() as s3:
                await s3.head_bucket(Bucket=self.bucket)
                logger.debug("Bucket already exists", bucket=self.bucket)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code in ("404", "NoSuchBucket", "403"):
                try:
                    async with self._get_s3_client() as s3:
                        create_bucket_config = {"Bucket": self.bucket}
                        await s3.create_bucket(**create_bucket_config)

                        logger.info("Bucket created and configured", bucket=self.bucket)
                except Exception:
                    logger.exception("Failed to create bucket", bucket=self.bucket)
                    raise
            else:
                logger.exception("Failed to access bucket", bucket=self.bucket)
                raise

    def _generate_public_url(self, object_key: str) -> str:
        """Generate public URL for object."""
        encoded_key = quote(object_key, safe="")

        return f"{self.public_url.rstrip('/')}/{self.bucket}/{encoded_key}"


class S3AvatarStorage(AvatarStorage, S3Client):
    """Async client for user avatar management using aioboto3.

    Stores avatars in S3-compatible storage.
    """

    @override
    async def ensure_bucket_exists(self) -> None:
        await super().ensure_bucket_exists()

        # make bucket public
        policy_json = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self.bucket}/*"],
                },
            ],
        }
        async with self._get_s3_client() as s3:
            await s3.put_bucket_policy(
                Bucket=self.bucket,
                Policy=json.dumps(policy_json),
            )
        logger.info("Bucket policy set to public-read", bucket=self.bucket)

    @override
    async def upload_avatar(
        self,
        user_id: UserId,
        file_data: BinaryIO,
        content_type: str,
    ) -> str:
        """Upload user avatar to storage."""
        object_key = self._get_avatar_key(user_id)

        try:
            async with self._get_s3_client() as s3:
                await s3.put_object(
                    Bucket=self.bucket,
                    Key=object_key,
                    Body=file_data,
                    ContentType=content_type,
                    ACL="public-read",
                )
        except Exception:
            logger.exception("Failed to upload avatar for user", user_id=user_id)
            raise
        else:
            return object_key

    @override
    async def delete_avatar(self, user_id: UserId) -> None:
        """Delete user avatar from storage."""
        object_key = self._get_avatar_key(user_id)
        await self._delete_object(object_key)
        logger.info("Avatar deleted for user", user_id=user_id)

    async def _delete_object(self, object_key: str) -> None:
        """Delete single object from storage."""
        async with self._get_s3_client() as s3:
            await s3.delete_object(Bucket=self.bucket, Key=object_key)

    @override
    def get_url(self, key: str) -> str:
        return self._generate_public_url(key)

    def _get_avatar_key(self, user_id: UserId) -> str:
        return f"avatars/{user_id}"
