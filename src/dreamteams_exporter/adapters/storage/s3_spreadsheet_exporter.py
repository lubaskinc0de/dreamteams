import csv
import io
import json
from collections.abc import Iterable
from typing import Any, override
from urllib.parse import quote

import aioboto3
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
_tracer = trace.get_tracer(__name__)


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
        csv.writer(sink).writerow(cells)
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
        """Flushes the tail as the final part, completes the multipart upload and returns the public URL."""
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
            ) as s3_client:
                await s3_client.complete_multipart_upload(
                    Bucket=self._config.bucket_name,
                    Key=self._key,
                    UploadId=self._upload_id,
                    MultipartUpload={"Parts": self._parts},
                )
        self._closed = True
        return self._public_url()

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
            ) as s3_client:
                await s3_client.abort_multipart_upload(
                    Bucket=self._config.bucket_name,
                    Key=self._key,
                    UploadId=self._upload_id,
                )
        self._closed = True

    def _public_url(self) -> str:
        base = self._config.public_url.rstrip("/")
        return f"{base}/{quote(self._key)}"


class CsvS3SpreadsheetExporter(SpreadsheetExporter):
    """Streams cell-row batches as UTF-8 CSV into S3 via multipart upload."""

    def __init__(self, config: S3Config) -> None:
        self._config = config
        self._aws_session = aioboto3.Session(
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        )

    async def ensure_bucket(self) -> None:
        """Creates the S3 bucket if it does not exist and applies a public-read policy."""
        with _tracer.start_as_current_span("dreamteams_exporter.s3.ensure_bucket") as span:
            span.set_attribute("dreamteams_exporter.s3.bucket", self._config.bucket_name)

            async with self._aws_session.client(
                service_name="s3",
                endpoint_url=self._config.endpoint_url,
                region_name=self._config.region,
            ) as s3_client:
                try:
                    await s3_client.create_bucket(Bucket=self._config.bucket_name)
                    bucket_created = True
                    span.set_attribute("dreamteams_exporter.s3.bucket_created", bucket_created)
                except ClientError as exc:
                    if exc.response.get("Error", {}).get("Code") != "BucketAlreadyOwnedByYou":
                        raise
                    bucket_created = False
                    span.set_attribute("dreamteams_exporter.s3.bucket_created", bucket_created)
                await s3_client.put_bucket_policy(
                    Bucket=self._config.bucket_name,
                    Policy=json.dumps(
                        {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Principal": "*",
                                    "Action": ["s3:GetObject"],
                                    "Resource": [f"arn:aws:s3:::{self._config.bucket_name}/*"],
                                },
                            ],
                        },
                    ),
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
