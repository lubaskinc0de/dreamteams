# ruff: noqa: RUF001 — the Russian column headers intentionally use Cyrillic letters.
import csv
import io
import json
from collections.abc import Iterable
from typing import Any, override
from urllib.parse import quote

import aioboto3

from dreamteams_exporter.adapters.storage.config import S3Config
from dreamteams_exporter.application.common.spreadsheet_exporter import (
    SpreadsheetExporter,
    SpreadsheetSession,
)
from dreamteams_exporter.entities.application.entity import Application
from dreamteams_exporter.entities.common.vo.participant_contact import ParticipantContact

_CONTENT_TYPE = "text/csv; charset=utf-8"
_PART_SIZE = 5 * 1024 * 1024  # S3's minimum for non-final multipart parts
_UTF8_BOM = b"\xef\xbb\xbf"  # lets Excel detect UTF-8 when opening the CSV

_HEADER_ROW: tuple[str, ...] = (
    "ID заявки",
    "Название соревнования",
    "Направления",
    "Статус",
    "Дата подачи",
    "Данные формы",
    "ID участника",
    "ФИО",
    "О себе",
    "Тип участника",
    "Возраст",
    "Контакты",
)


def _format_contacts(contacts: list[ParticipantContact]) -> str:
    return ", ".join(f"{c.title}: {c.url}" for c in contacts)


def _row_for(application: Application) -> tuple[str, ...]:
    return (
        str(application.id),
        application.competition_name,
        ", ".join(application.domains),
        application.status.value,
        application.created_at.isoformat(),
        json.dumps(application.form_data, ensure_ascii=False) if application.form_data is not None else "",
        str(application.participant.id),
        application.participant.full_name,
        application.participant.bio or "",
        application.participant.participant_type,
        str(application.participant.age),
        _format_contacts(application.participant.contacts),
    )


class CsvS3SpreadsheetSession(SpreadsheetSession):
    """CSV + S3 multipart session: batches are serialised into the buffer and parts flush to S3 as they fill."""

    def __init__(
        self,
        aws_session: aioboto3.Session,
        config: S3Config,
        key: str,
        upload_id: str,
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
        self._encode_row(_HEADER_ROW)

    def _encode_row(self, row: tuple[str, ...]) -> None:
        sink = io.StringIO()
        csv.writer(sink).writerow(row)
        self._buffer.extend(sink.getvalue().encode("utf-8"))

    @override
    async def write_rows(self, rows: Iterable[Application]) -> None:
        """Encodes rows into CSV lines and flushes full parts to S3 when the buffer crosses the threshold."""
        for application in rows:
            self._encode_row(_row_for(application))

        while len(self._buffer) >= _PART_SIZE:
            part = bytes(self._buffer[:_PART_SIZE])
            del self._buffer[:_PART_SIZE]
            await self._upload_part(part)

    async def _upload_part(self, data: bytes) -> None:
        async with self._aws_session.client(
            service_name="s3",
            endpoint_url=self._config.endpoint_url,
            region_name=self._config.region,
        ) as s3_client:
            response = await s3_client.upload_part(
                Bucket=self._config.bucket_name,
                Key=self._key,
                UploadId=self._upload_id,
                PartNumber=self._part_number,
                Body=data,
            )
        self._parts.append({"PartNumber": self._part_number, "ETag": response["ETag"]})
        self._part_number += 1

    @override
    async def finish(self) -> str:
        """Flushes the tail as the final part, completes the multipart upload and returns the public URL."""
        if self._closed:
            msg = "SpreadsheetSession already closed"
            raise RuntimeError(msg)

        await self._upload_part(bytes(self._buffer))
        self._buffer.clear()

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
    """Exports applications as UTF-8 CSV, streamed to S3 via multipart upload as rows arrive."""

    def __init__(self, config: S3Config) -> None:
        self._config = config
        self._aws_session = aioboto3.Session(
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        )

    @override
    async def start(self, *, key: str) -> SpreadsheetSession:
        """Creates an S3 multipart upload and returns a session ready to accept rows."""
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
        return CsvS3SpreadsheetSession(self._aws_session, self._config, key, create["UploadId"])
