from __future__ import annotations
import time

from celery import Celery
from celery.utils.log import get_task_logger

from config.settings import CELERY
import utils.cache as cache

celery_app = Celery("ai_resume")
celery_app.config_from_object(CELERY)

celery_app.autodiscover_tasks(["backend.workers"])

logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    name="workers.tasks.parse_resume_task",
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def parse_resume_task(self, resume_id: int) -> dict:
    task_id = self.request.id

    logger.info(
        "[parse_resume] START resume_id=%s task_id=%s",
        resume_id,
        task_id,
    )

    cache.set_task_status(task_id, "processing")

    t0 = time.monotonic()

    try:
        from services.resume_service import ResumeService

        ResumeService().finalize_parse(resume_id)

        elapsed = int((time.monotonic() - t0) * 1000)

        result = {
            "resume_id": resume_id,
            "status": "completed",
            "ms": elapsed,
        }

        cache.set_task_status(task_id, "completed", result)

        logger.info(
            "[parse_resume] DONE resume_id=%s ms=%d",
            resume_id,
            elapsed,
        )

        return result

    except Exception as exc:
        logger.exception(
            "[parse_resume] FAILED resume_id=%s: %s",
            resume_id,
            exc,
        )

        cache.set_task_status(
            task_id,
            "failed",
            {"error": str(exc)},
        )

        try:
            raise self.retry(exc=exc)

        except self.MaxRetriesExceededError:
            logger.error(
                "[parse_resume] MAX RETRIES EXCEEDED resume_id=%s",
                resume_id,
            )

            return {
                "resume_id": resume_id,
                "status": "failed",
                "error": str(exc),
            }


@celery_app.task(
    bind=True,
    name="workers.tasks.run_evaluation_task",
    max_retries=2,
    default_retry_delay=15,
    acks_late=True,
    soft_time_limit=120,
    time_limit=180,
)
def run_evaluation_task(self, eval_id: int) -> dict:
    task_id = self.request.id

    logger.info(
        "[run_evaluation] START eval_id=%s task_id=%s",
        eval_id,
        task_id,
    )

    cache.set_task_status(task_id, "processing")

    t0 = time.monotonic()

    try:
        from services.evaluation_orchestrator import (
            EvaluationOrchestrator,
        )

        EvaluationOrchestrator().finalize(eval_id)

        elapsed = int((time.monotonic() - t0) * 1000)

        result = {
            "evaluation_id": eval_id,
            "status": "completed",
            "ms": elapsed,
        }

        cache.set_task_status(task_id, "completed", result)

        logger.info(
            "[run_evaluation] DONE eval_id=%s ms=%d",
            eval_id,
            elapsed,
        )

        return result

    except Exception as exc:
        logger.exception(
            "[run_evaluation] FAILED eval_id=%s: %s",
            eval_id,
            exc,
        )

        cache.set_task_status(
            task_id,
            "failed",
            {"error": str(exc)},
        )

        try:
            raise self.retry(exc=exc)

        except self.MaxRetriesExceededError:
            logger.error(
                "[run_evaluation] MAX RETRIES EXCEEDED eval_id=%s",
                eval_id,
            )

            return {
                "evaluation_id": eval_id,
                "status": "failed",
                "error": str(exc),
            }


def get_task_result(task_id: str) -> dict:
    redis_status = cache.get_task_status(task_id)

    if redis_status:
        return redis_status

    async_result = celery_app.AsyncResult(task_id)

    return {
        "status": async_result.status.lower(),
        "result": (
            async_result.result
            if async_result.ready()
            else None
        ),
    }