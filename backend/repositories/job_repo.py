
from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models.orm import (
    Job,
)

from backend.utils.errors import (
    NotFoundError,
)

from backend.utils.logger import (
    get_logger,
)

logger = get_logger(__name__)


class JobRepository:

    def __init__(
        self,
        session: Session,
    ):
        self._s = session

    def create(
        self,
        *,
        title: str,
        description: str,
        company: str | None = None,
        required_skills: list[str] | None = None,
        created_by: int | None = None,
    ) -> Job:

        job = Job(
            title=title,
            description=description,
            company=company,
            required_skills=(
                required_skills or []
            ),
            created_by=created_by,
        )

        self._s.add(job)

        self._s.flush()

        logger.info(
            (
                "Job created "
                "id=%s title='%s'"
            ),
            job.id,
            title,
        )

        return job

    def update(
        self,
        job_id: int,
        **fields,
    ) -> Job:

        job = self._get_or_raise(
            job_id
        )

        allowed = {
            "title",
            "description",
            "company",
            "required_skills",
        }

        for key, value in fields.items():

            if key in allowed:
                setattr(
                    job,
                    key,
                    value,
                )

        return job

    def delete(
        self,
        job_id: int,
    ) -> None:

        job = self._get_or_raise(
            job_id
        )

        self._s.delete(job)

        logger.info(
            "Job deleted id=%s",
            job_id,
        )

    def get_by_id(
        self,
        job_id: int,
    ) -> Job:

        return self._get_or_raise(
            job_id
        )

    def list_all(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> list[Job]:

        return (
            self._s.query(Job)
            .order_by(
                Job.created_at.desc()
            )
            .offset(
                (page - 1) * per_page
            )
            .limit(per_page)
            .all()
        )

    def list_by_creator(
        self,
        user_id: int,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> list[Job]:

        return (
            self._s.query(Job)
            .filter(
                Job.created_by == user_id
            )
            .order_by(
                Job.created_at.desc()
            )
            .offset(
                (page - 1) * per_page
            )
            .limit(per_page)
            .all()
        )

    def count_all(self) -> int:

        return (
            self._s.query(Job)
            .count()
        )

    def _get_or_raise(
        self,
        job_id: int,
    ) -> Job:

        job = self._s.get(
            Job,
            job_id,
        )

        if not job:
            raise NotFoundError(
                f"Job {job_id} not found."
            )

        return job