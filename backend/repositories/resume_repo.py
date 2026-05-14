from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from.models.orm import (
    Resume,
    JobStatus,
)

from.utils.errors import (
    NotFoundError,
)

from.utils.logger import (
    get_logger,
)

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


class ResumeRepository:

    def __init__(
        self,
        session: Session,
    ):
        self._s = session

    def create(
        self,
        *,
        user_id: int | None,
        original_name: str,
        stored_path: str,
        file_type: str,
    ) -> Resume:

        resume = Resume(
            user_id=user_id,
            original_name=original_name,
            stored_path=stored_path,
            file_type=file_type,
            parse_status=JobStatus.PENDING,
        )

        self._s.add(resume)

        self._s.flush()

        logger.info(
            "Resume created id=%s user=%s",
            resume.id,
            user_id,
        )

        return resume

    def mark_processing(
        self,
        resume_id: int,
        task_id: str,
    ) -> None:

        r = self._get_or_raise(
            resume_id
        )

        r.parse_status = (
            JobStatus.PROCESSING
        )

        r.parse_task_id = task_id

    def mark_parsed(
        self,
        resume_id: int,
        *,
        parsed_text: str,
        skills_found: list[str],
        word_count: int,
    ) -> None:

        r = self._get_or_raise(
            resume_id
        )

        r.parsed_text = parsed_text

        r.skills_found = skills_found

        r.word_count = word_count

        r.parse_status = (
            JobStatus.COMPLETED
        )

    def mark_failed(
        self,
        resume_id: int,
        error: str,
    ) -> None:

        r = self._get_or_raise(
            resume_id
        )

        r.parse_status = (
            JobStatus.FAILED
        )

        r.parse_task_id = (
            f"ERR:{error[:60]}"
        )

    def get_by_id(
        self,
        resume_id: int,
    ) -> Resume:

        return self._get_or_raise(
            resume_id
        )

    def list_by_user(
        self,
        user_id: int,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> list[Resume]:

        return (
            self._s.query(Resume)
            .filter(
                Resume.user_id == user_id
            )
            .order_by(
                Resume.uploaded_at.desc()
            )
            .offset(
                (page - 1) * per_page
            )
            .limit(per_page)
            .all()
        )

    def count_by_user(
        self,
        user_id: int,
    ) -> int:

        return (
            self._s.query(Resume)
            .filter(
                Resume.user_id == user_id
            )
            .count()
        )

    def _get_or_raise(
        self,
        resume_id: int,
    ) -> Resume:

        r = self._s.get(
            Resume,
            resume_id,
        )

        if r is None:
            raise NotFoundError(
                (
                    f"Resume {resume_id} "
                    "not found."
                )
            )

        return r