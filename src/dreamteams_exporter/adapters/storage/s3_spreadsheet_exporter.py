import csv
import io
from collections.abc import Iterable
from typing import Any, cast, override

import aioboto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError
from opentelemetry import trace

from dreamteams_exporter.adapters.storage.config import S3Config
from dreamteams_exporter.application.common.dto.export_row import ExportRow
from dreamteams_exporter.application.common.spreadsheet_exporter import (
    SpreadsheetExporter,
    SpreadsheetSession,
)

_CONTENT_TYPE = "text/csv; charset=utf-8"
_PART_SIZE = 5 * 1024 * 1024  # S3's minimum for non-final multipart parts
_UTF8_BOM = b"\xef\xbb\xbf"  # lets Excel detect UTF-8 when opening the CSV
_EXPORTS_PREFIX = "exports/"
_DANGEROUS_CSV_PREFIXES = ("=", "+", "-", "@")
_DANGEROUS_LEADING_CHARS = ("\t", "\r", "\n")
_S3_CLIENT_CONFIG = BotoConfig(signature_version="s3v4", s3={"addressing_style": "path"})
_BUCKET_MISSING_ERROR_CODES = frozenset({"404", "NoSuchBucket", "NotFound"})
_BUCKET_ALREADY_EXISTS_ERROR_CODES = frozenset({"BucketAlreadyOwnedByYou", "BucketAlreadyExists"})
_tracer = trace.get_tracer(__name__)


def escape_csv_cell(cell: str) -> str:
    """Prefix spreadsheet formula-like cells so CSV consumers treat them as literal text."""
    if not cell:
        return cell
    stripped = cell.lstrip()
    if cell[0] in _DANGEROUS_LEADING_CHARS or (stripped and stripped[0] in _DANGEROUS_CSV_PREFIXES):
        return f"'{cell}"
    return cell


class CsvS3SpreadsheetSession(SpreadsheetSession):
    """CSV + S3 multipart session: batches are serialised into the buffer and parts flush to S3 as they fill."""

    def __init__(
        self,
        aws_session: aioboto3.Session,
        config: S3Config,
        key: str,
        upload_id: str,
        headers: list[str],
    ) -> None:
        self._aws_session = aws_session
        self._config = config
        self._key = key
        self._upload_id = upload_id
        self._buffer = bytearray()
        self._part_number = 1
        self._parts: list[dict[str, Any]] = []
        self._closed = False
        self._buffer.extend(_UTF8_BOM)
        self._encode_cells(headers)

    def _encode_cells(self, cells: list[str]) -> None:
        sink = io.StringIO()
        csv.writer(sink).writerow([escape_csv_cell(cell) for cell in cells])
        self._buffer.extend(sink.getvalue().encode("utf-8"))

    @override
    async def write_rows(self, rows: Iterable[ExportRow]) -> None:
        """Serialises rows into CSV lines and flushes full 5 MB parts to S3 as the buffer fills."""
        for row in rows:
            self._encode_cells(row)

        while len(self._buffer) >= _PART_SIZE:
            part = bytes(self._buffer[:_PART_SIZE])
            del self._buffer[:_PART_SIZE]
            await self._upload_part(part)

    async def _upload_part(self, data: bytes) -> None:
        part_number = self._part_number
        with _tracer.start_as_current_span("dreamteams_exporter.s3.upload_part") as span:
            span.set_attribute("dreamteams_exporter.s3.bucket", self._config.bucket_name)
            span.set_attribute("dreamteams_exporter.s3.key", self._key)
            span.set_attribute("dreamteams_exporter.s3.part_number", part_number)
            span.set_attribute("dreamteams_exporter.s3.part_size_bytes", len(data))

            async with self._aws_session.client(
                service_name="s3",
                endpoint_url=self._config.endpoint_url,
                region_name=self._config.region,
                config=_S3_CLIENT_CONFIG,
            ) as s3_client:
                response = await s3_client.upload_part(
                    Bucket=self._config.bucket_name,
                    Key=self._key,
                    UploadId=self._upload_id,
                    PartNumber=part_number,
                    Body=data,
                )
        self._parts.append({"PartNumber": part_number, "ETag": response["ETag"]})
        self._part_number += 1

    @override
    async def finish(self) -> str:
        """Flushes the tail as the final part, completes the multipart upload and returns the private object key."""
        if self._closed:
            msg = "SpreadsheetSession already closed"
            raise RuntimeError(msg)

        await self._upload_part(bytes(self._buffer))
        self._buffer.clear()

        with _tracer.start_as_current_span("dreamteams_exporter.s3.complete_multipart_upload") as span:
            span.set_attribute("dreamteams_exporter.s3.bucket", self._config.bucket_name)
            span.set_attribute("dreamteams_exporter.s3.key", self._key)
            span.set_attribute("dreamteams_exporter.s3.parts_count", len(self._parts))

            async with self._aws_session.client(
                service_name="s3",
                endpoint_url=self._config.endpoint_url,
                region_name=self._config.region,
                config=_S3_CLIENT_CONFIG,
            ) as s3_client:
                await s3_client.complete_multipart_upload(
                    Bucket=self._config.bucket_name,
                    Key=self._key,
                    UploadId=self._upload_id,
                    MultipartUpload={"Parts": self._parts},
                )
        self._closed = True
        return self._key

    @override
    async def abort(self) -> None:
        """Aborts the S3 multipart upload, releasing any parts already uploaded."""
        if self._closed:
            return
        with _tracer.start_as_current_span("dreamteams_exporter.s3.abort_multipart_upload") as span:
            span.set_attribute("dreamteams_exporter.s3.bucket", self._config.bucket_name)
            span.set_attribute("dreamteams_exporter.s3.key", self._key)
            span.set_attribute("dreamteams_exporter.s3.parts_count", len(self._parts))

            async with self._aws_session.client(
                service_name="s3",
                endpoint_url=self._config.endpoint_url,
                region_name=self._config.region,
                config=_S3_CLIENT_CONFIG,
            ) as s3_client:
                await s3_client.abort_multipart_upload(
                    Bucket=self._config.bucket_name,
                    Key=self._key,
                    UploadId=self._upload_id,
                )
        self._closed = True


class CsvS3SpreadsheetExporter(SpreadsheetExporter):
    """Streams cell-row batches as UTF-8 CSV into S3 via multipart upload."""

    def __init__(self, config: S3Config) -> None:
        self._config = config
        self._aws_session = aioboto3.Session(
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        )

    async def ensure_bucket(self) -> None:
        """Creates the S3 bucket if it does not exist, keeps it private, and applies export expiry."""
        with _tracer.start_as_current_span("dreamteams_exporter.s3.ensure_bucket") as span:
            span.set_attribute("dreamteams_exporter.s3.bucket", self._config.bucket_name)

            async with self._aws_session.client(
                service_name="s3",
                endpoint_url=self._config.endpoint_url,
                region_name=self._config.region,
                config=_S3_CLIENT_CONFIG,
            ) as s3_client:
                try:
                    await s3_client.head_bucket(Bucket=self._config.bucket_name)
                    bucket_created = False
                except ClientError as exc:
                    if exc.response.get("Error", {}).get("Code") not in _BUCKET_MISSING_ERROR_CODES:
                        raise
                    try:
                        await s3_client.create_bucket(Bucket=self._config.bucket_name)
                        bucket_created = True
                    except ClientError as create_exc:
                        if (
                            create_exc.response.get("Error", {}).get("Code")
                            not in _BUCKET_ALREADY_EXISTS_ERROR_CODES
                        ):
                            raise
                        await s3_client.head_bucket(Bucket=self._config.bucket_name)
                        bucket_created = False
                span.set_attribute("dreamteams_exporter.s3.bucket_created", bucket_created)
                try:
                    await s3_client.delete_bucket_policy(Bucket=self._config.bucket_name)
                    bucket_policy_deleted = True
                    span.set_attribute("dreamteams_exporter.s3.bucket_policy_deleted", bucket_policy_deleted)
                except ClientError as exc:
                    if exc.response.get("Error", {}).get("Code") != "NoSuchBucketPolicy":
                        raise
                    bucket_policy_deleted = False
                    span.set_attribute("dreamteams_exporter.s3.bucket_policy_deleted", bucket_policy_deleted)
                await s3_client.put_bucket_lifecycle_configuration(
                    Bucket=self._config.bucket_name,
                    LifecycleConfiguration={
                        "Rules": [
                            {
                                "ID": "expire-exported-files",
                                "Status": "Enabled",
                                "Filter": {"Prefix": _EXPORTS_PREFIX},
                                "Expiration": {"Days": self._config.export_file_lifetime_days},
                            },
                        ],
                    },
                )

    @override
    async def start(self, *, key: str, headers: list[str]) -> SpreadsheetSession:
        """Creates an S3 multipart upload, seeds the header row, and returns a session ready to accept rows."""
        with _tracer.start_as_current_span("dreamteams_exporter.s3.start_multipart_upload") as span:
            span.set_attribute("dreamteams_exporter.s3.bucket", self._config.bucket_name)
            span.set_attribute("dreamteams_exporter.s3.key", key)
            span.set_attribute("dreamteams_exporter.s3.headers_count", len(headers))

            async with self._aws_session.client(
                service_name="s3",
                endpoint_url=self._config.endpoint_url,
                region_name=self._config.region,
                config=_S3_CLIENT_CONFIG,
            ) as s3_client:
                create = await s3_client.create_multipart_upload(
                    Bucket=self._config.bucket_name,
                    Key=key,
                    ContentType=_CONTENT_TYPE,
                )
        return CsvS3SpreadsheetSession(
            self._aws_session,
            self._config,
            key,
            create["UploadId"],
            headers,
        )

    @override
    async def get_download_url(self, key: str) -> str:
        """Generate a short-lived signed URL for a private exported file."""
        async with self._aws_session.client(
            service_name="s3",
            endpoint_url=self._config.download_endpoint_url,
            region_name=self._config.region,
            config=_S3_CLIENT_CONFIG,
        ) as s3_client:
            return cast(
                "str",
                await s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self._config.bucket_name, "Key": key},
                    ExpiresIn=self._config.presigned_url_ttl_seconds,
                ),
            )
