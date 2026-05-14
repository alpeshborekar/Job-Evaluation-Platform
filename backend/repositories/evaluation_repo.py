from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.orm import (
    Evaluation,
    JobStatus,
    Recommendation,
)

from backend.utils.errors import (
    NotFoundError,
)

from backend.utils.logger import (
    get_logger,
)

logger = get_logger(__name__)


class EvaluationRepository:

    def __init__(
        self,
        session: Session,
    ):
        self._s = session

    def create(
        self,
        *,
        resume_id: int,
        job_id: int,
        user_id: int | None,
    ) -> Evaluation:

        ev = Evaluation(
            resume_id=resume_id,
            job_id=job_id,
            user_id=user_id,
            status=JobStatus.PENDING,
        )

        self._s.add(ev)

        self._s.flush()

        logger.info(
            (
                "Evaluation created "
                "id=%s resume=%s job=%s"
            ),
            ev.id,
            resume_id,
            job_id,
        )

        return ev

    def mark_processing(
        self,
        eval_id: int,
        task_id: str,
    ) -> None:

        e = self._get_or_raise(
            eval_id
        )

        e.status = (
            JobStatus.PROCESSING
        )

        e.task_id = task_id

    def mark_completed(
        self,
        eval_id: int,
        *,
        result: "EvalResult",
    ) -> None:

        e = self._get_or_raise(
            eval_id
        )

        e.status = (
            JobStatus.COMPLETED
        )

        e.total_score = (
            result.total_score
        )

        e.skills_score = (
            result.skills_score
        )

        e.experience_score = (
            result.experience_score
        )

        e.keyword_score = (
            result.keyword_score
        )

        e.matched_skills = (
            result.matched_skills
        )

        e.missing_skills = (
            result.missing_skills
        )

        e.recommendation = (
            Recommendation(
                result.recommendation
            )
        )

        e.reasoning = (
            result.reasoning
        )

        e.ai_feedback = (
            result.ai_feedback
        )

        e.completed_at = (
            datetime.utcnow()
        )

    def mark_failed(
        self,
        eval_id: int,
        error: str,
    ) -> None:

        e = self._get_or_raise(
            eval_id
        )

        e.status = (
            JobStatus.FAILED
        )

        e.error_detail = error

        e.completed_at = (
            datetime.utcnow()
        )

    def get_by_id(
        self,
        eval_id: int,
    ) -> Evaluation:

        return self._get_or_raise(
            eval_id
        )

    def find_by_resume_and_job(
        self,
        resume_id: int,
        job_id: int,
    ) -> Evaluation | None:

        return (
            self._s.query(Evaluation)
            .filter(
                Evaluation.resume_id
                == resume_id,

                Evaluation.job_id
                == job_id,

                Evaluation.status
                == JobStatus.COMPLETED,
            )
            .order_by(
                Evaluation.completed_at.desc()
            )
            .first()
        )

    def list_by_user(
        self,
        user_id: int,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> list[Evaluation]:

        return (
            self._s.query(Evaluation)
            .filter(
                Evaluation.user_id
                == user_id
            )
            .order_by(
                Evaluation.created_at.desc()
            )
            .offset(
                (page - 1) * per_page
            )
            .limit(per_page)
            .all()
        )

    def _get_or_raise(
        self,
        eval_id: int,
    ) -> Evaluation:

        e = self._s.get(
            Evaluation,
            eval_id,
        )

        if e is None:
            raise NotFoundError(
                (
                    f"Evaluation {eval_id} "
                    "not found."
                )
            )

        return e