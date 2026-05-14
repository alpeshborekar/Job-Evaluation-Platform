"""
services/job_service.py
Business logic for job postings.
Extracts required skills from job descriptions so evaluations
can use them directly without re-parsing every time.
"""

from __future__ import annotations

from backend.utils.database import (
    db_session,
)

from backend.utils.errors import (
    AuthorizationError,
)

from backend.utils.logger import (
    get_logger,
)

from backend.repositories.job_repo import (
    JobRepository,
)

logger = get_logger(__name__)


class JobService:

    def create(
        self,
        *,
        title: str,
        description: str,
        company: str | None = None,
        created_by: int | None = None,
    ) -> dict:
        """
        Extract skills from the JD,
        then persist the job.
        """

        required_skills = (
            self._extract_skills(
                description
            )
        )

        with db_session() as session:

            job = JobRepository(
                session
            ).create(
                title=title,
                description=description,
                company=company,
                required_skills=required_skills,
                created_by=created_by,
            )

            payload = self._serialize(
                job
            )

        logger.info(
            (
                "Job created "
                "id=%s "
                "skills_extracted=%d"
            ),
            payload["id"],
            len(required_skills),
        )

        return payload

    def get(
        self,
        job_id: int,
    ) -> dict:

        with db_session() as session:

            job = JobRepository(
                session
            ).get_by_id(
                job_id
            )

            return self._serialize(
                job
            )

    def list(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:

        with db_session() as session:

            repo = JobRepository(
                session
            )

            jobs = repo.list_all(
                page=page,
                per_page=per_page,
            )

            total = repo.count_all()

            return {
                "items": [
                    self._serialize(j)
                    for j in jobs
                ],
                "total": total,
                "page": page,
                "per_page": per_page,
            }

    def delete(
        self,
        job_id: int,
        *,
        requesting_user_id: int | None,
    ) -> None:

        with db_session() as session:

            repo = JobRepository(
                session
            )

            job = repo.get_by_id(
                job_id
            )

            if (
                requesting_user_id
                and job.created_by
                != requesting_user_id
            ):
                raise AuthorizationError(
                    (
                        "You can only delete "
                        "your own job postings."
                    )
                )

            repo.delete(job_id)

    @staticmethod
    def _extract_skills(
        text: str,
    ) -> list[str]:

        import re

        multi = re.findall(
            (
                r"\b(?:machine learning|"
                r"deep learning|"
                r"natural language processing|"
                r"data science|"
                r"computer vision|"
                r"cloud computing|"
                r"devops|"
                r"ci[/\s]?cd|"
                r"rest api|"
                r"react\.?js|"
                r"node\.?js|"
                r"next\.?js|"
                r"vue\.?js|"
                r"spring boot|"
                r"\.net core|"
                r"asp\.net|"
                r"aws|gcp|azure|"
                r"docker|"
                r"kubernetes|"
                r"terraform|"
                r"postgresql|"
                r"mongodb|"
                r"redis|"
                r"elasticsearch|"
                r"kafka|"
                r"rabbitmq)\b"
            ),
            text.lower(),
        )

        singles = re.findall(
            (
                r"\b(?:Python|"
                r"JavaScript|"
                r"TypeScript|"
                r"Java|Go|Rust|"
                r"C\+\+|C#|"
                r"Flask|Django|"
                r"FastAPI|"
                r"React|Angular|Vue|"
                r"SQL|NoSQL|"
                r"Git|Linux|"
                r"Bash|HTML|CSS|"
                r"GraphQL|"
                r"TensorFlow|"
                r"PyTorch|"
                r"Pandas|NumPy|"
                r"Spark|Hadoop|"
                r"Celery|Nginx|"
                r"Gunicorn|"
                r"Terraform)\b"
            ),
            text,
        )

        return sorted(
            {
                s.lower().strip()
                for s in (
                    multi + singles
                )
            }
        )

    @staticmethod
    def _serialize(job) -> dict:

        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "description": (
                job.description
            ),
            "required_skills": (
                job.required_skills
                or []
            ),
            "created_by": (
                job.created_by
            ),
            "created_at": (
                job.created_at.isoformat()
                if job.created_at
                else None
            ),
        }