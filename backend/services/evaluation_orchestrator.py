from __future__ import annotations

from backend.utils.database import (
    db_session,
)

from backend.utils.errors import (
    NotFoundError,
    ProcessingError,
)

from backend.utils.logger import (
    get_logger,
)

from backend.repositories.evaluation_repo import (
    EvaluationRepository,
)

from backend.repositories.resume_repo import (
    ResumeRepository,
)

from backend.models.orm import (
    JobStatus,
)

logger = get_logger(__name__)


class EvaluationOrchestrator:

    def submit(
        self,
        *,
        resume_id: int,
        job_id: int,
        user_id: int | None,
    ) -> dict:

        with db_session() as session:

            resume = ResumeRepository(
                session
            ).get_by_id(
                resume_id
            )

            if (
                resume.parse_status
                != JobStatus.COMPLETED
            ):
                raise ProcessingError(
                    (
                        "Resume has not been "
                        "parsed yet. "
                        f"Current status: "
                        f"{resume.parse_status.value}"
                    )
                )

            ev = EvaluationRepository(
                session
            ).create(
                resume_id=resume_id,
                job_id=job_id,
                user_id=user_id,
            )

            eval_id = ev.id

        from backend.workers.tasks import (
            run_evaluation_task,
        )

        task = run_evaluation_task.delay(
            eval_id
        )

        with db_session() as session:

            EvaluationRepository(
                session
            ).mark_processing(
                eval_id,
                task.id,
            )

        logger.info(
            (
                "Evaluation queued "
                "eval_id=%s "
                "resume=%s "
                "job=%s "
                "task_id=%s"
            ),
            eval_id,
            resume_id,
            job_id,
            task.id,
        )

        return {
            "evaluation_id": eval_id,
            "task_id": task.id,
            "status": "pending",
        }

    def get(
        self,
        eval_id: int,
        *,
        requesting_user_id: int | None = None,
    ) -> dict:

        with db_session() as session:

            ev = EvaluationRepository(
                session
            ).get_by_id(
                eval_id
            )

            self._check_ownership(
                ev,
                requesting_user_id,
            )

            if (
                ev.status
                == JobStatus.COMPLETED
            ):
                return self._serialize(
                    ev
                )

            return {
                "evaluation_id": ev.id,
                "status": (
                    ev.status.value
                ),
                "task_id": ev.task_id,
                "error": (
                    ev.error_detail
                ),
            }

    def finalize(
        self,
        eval_id: int,
    ) -> None:

        from backend.services.evaluation_service import (
            EvaluationService,
        )

        from backend.models.orm import (
            Job,
        )

        with db_session() as session:

            ev = EvaluationRepository(
                session
            ).get_by_id(
                eval_id
            )

            resume = ResumeRepository(
                session
            ).get_by_id(
                ev.resume_id
            )

            job = session.get(
                Job,
                ev.job_id,
            )

            if not job:
                raise NotFoundError(
                    f"Job {ev.job_id} not found."
                )

            if not resume.parsed_text:
                raise ProcessingError(
                    (
                        "Resume text is empty "
                        "— re-upload and retry."
                    )
                )

            try:

                logger.info(
                    (
                        "Resume skills being sent "
                        "to evaluation: %s"
                    ),
                    resume.skills_found,
                )

                result = (
                    EvaluationService()
                    .evaluate(
                        resume_text=(
                            resume.parsed_text
                        ),
                        job_description=(
                            job.description
                        ),
                        resume_skills=(
                            resume.skills_found
                            or []
                        ),
                    )
                )

                EvaluationRepository(
                    session
                ).mark_completed(
                    eval_id,
                    result=result,
                )

                logger.info(
                    (
                        "Evaluation finalised "
                        "eval_id=%s "
                        "score=%.1f "
                        "rec=%s"
                    ),
                    eval_id,
                    result.total_score,
                    result.recommendation,
                )

            except Exception as exc:

                EvaluationRepository(
                    session
                ).mark_failed(
                    eval_id,
                    str(exc),
                )

                logger.exception(
                    (
                        "Evaluation failed "
                        "eval_id=%s"
                    ),
                    eval_id,
                )

                raise

    @staticmethod
    def _check_ownership(
        ev,
        user_id: int | None,
    ) -> None:

        if (
            user_id
            and ev.user_id
            and ev.user_id != user_id
        ):

            from backend.utils.errors import (
                AuthorizationError,
            )

            raise AuthorizationError(
                (
                    "Access denied to "
                    "this evaluation."
                )
            )

    @staticmethod
    def _serialize(ev) -> dict:

        return {
            "evaluation_id": ev.id,
            "status": (
                ev.status.value
            ),
            "resume_id": ev.resume_id,
            "job_id": ev.job_id,
            "total_score": (
                ev.total_score
            ),
            "skills_score": (
                ev.skills_score
            ),
            "experience_score": (
                ev.experience_score
            ),
            "keyword_score": (
                ev.keyword_score
            ),
            "matched_skills": (
                ev.matched_skills
                or []
            ),
            "missing_skills": (
                ev.missing_skills
                or []
            ),
            "recommendation": (
                ev.recommendation.value
                if ev.recommendation
                else None
            ),
            "reasoning": (
                ev.reasoning
            ),
            "ai_feedback": (
                ev.ai_feedback
            ),
            "completed_at": (
                ev.completed_at.isoformat()
                if ev.completed_at
                else None
            ),
        }