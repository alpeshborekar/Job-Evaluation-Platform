from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

import pdfminer.high_level
import docx

from config.settings import APP

from utils.errors import (
    UnsupportedFileTypeError,
    FileTooLargeError,
    ProcessingError,
)

from utils.logger import (
    get_logger,
)

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
}

MAX_BYTES = (
    APP.max_upload_mb
    * 1024
    * 1024
)


@dataclass
class ParseResult:
    text: str
    word_count: int
    file_type: str
    stored_path: str


def save_upload(
    file_storage,
) -> tuple[str, str]:
    """
    Validate and persist an uploaded file.
    Returns:
        (stored_path, file_ext)
    """

    original: str = (
        file_storage.filename
        or ""
    )

    ext = (
        original.rsplit(".", 1)[-1].lower()
        if "." in original
        else ""
    )

    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            (
                f"'{ext}' is not supported. "
                "Upload a PDF or DOCX."
            ),
            {
                "allowed": list(
                    ALLOWED_EXTENSIONS
                )
            },
        )

    file_storage.seek(0, 2)

    size = file_storage.tell()

    file_storage.seek(0)

    if size > MAX_BYTES:
        raise FileTooLargeError(
            (
                f"File exceeds "
                f"{APP.max_upload_mb} MB limit."
            ),
            {
                "max_mb": APP.max_upload_mb,
                "received_mb": round(
                    size / 1024 / 1024,
                    2,
                ),
            },
        )

    os.makedirs(
        APP.upload_dir,
        exist_ok=True,
    )

    filename = (
        f"{uuid.uuid4().hex}.{ext}"
    )

    path = os.path.join(
        APP.upload_dir,
        filename,
    )

    file_storage.save(path)

    logger.info(
        "File saved: %s (%d bytes)",
        path,
        size,
    )

    return path, ext


def parse_file(
    stored_path: str,
    file_type: str,
) -> ParseResult:
    """
    Extract text from a saved file.
    """

    try:

        if file_type == "pdf":
            text = _parse_pdf(
                stored_path
            )

        elif file_type == "docx":
            text = _parse_docx(
                stored_path
            )

        else:
            raise UnsupportedFileTypeError(
                f"Cannot parse .{file_type}"
            )

        text = _clean_text(text)

        return ParseResult(
            text=text,
            word_count=len(
                text.split()
            ),
            file_type=file_type,
            stored_path=stored_path,
        )

    except (
        UnsupportedFileTypeError,
        FileTooLargeError,
    ):
        raise

    except Exception as exc:
        logger.exception(
            "Failed to parse %s",
            stored_path,
        )

        raise ProcessingError(
            f"Could not extract text: {exc}"
        ) from exc


def _parse_pdf(path: str) -> str:
    return (
        pdfminer.high_level.extract_text(
            path
        )
        or ""
    )


def _parse_docx(path: str) -> str:
    doc = docx.Document(path)

    return "\n".join(
        p.text for p in doc.paragraphs
    )


def _clean_text(text: str) -> str:
    import re

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()