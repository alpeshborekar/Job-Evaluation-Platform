from __future__ import annotations
import json
import hashlib
from typing import Any

import redis

from.config.settings import REDIS
from.utils.logger import get_logger

logger = get_logger(__name__)

_pool = redis.ConnectionPool.from_url(
    REDIS.url,
    max_connections=20,
    decode_responses=True,
)


def _client() -> redis.Redis:
    return redis.Redis(connection_pool=_pool)


def _eval_key(resume_id: int, job_id: int) -> str:
    return f"eval:{resume_id}:{job_id}"


def _resume_key(resume_id: int) -> str:
    return f"resume:meta:{resume_id}"


def _task_key(task_id: str) -> str:
    return f"task:status:{task_id}"


def get(key: str) -> Any | None:
    try:
        raw = _client().get(key)

        return json.loads(raw) if raw is not None else None

    except Exception as e:
        logger.warning(
            "Cache GET failed for key=%s: %s",
            key,
            e,
        )

        return None


def set(key: str, value: Any, ttl: int) -> bool:
    try:
        _client().setex(key, ttl, json.dumps(value))

        return True

    except Exception as e:
        logger.warning(
            "Cache SET failed for key=%s: %s",
            key,
            e,
        )

        return False


def delete(key: str) -> None:
    try:
        _client().delete(key)

    except Exception as e:
        logger.warning(
            "Cache DELETE failed for key=%s: %s",
            key,
            e,
        )


def invalidate_pattern(pattern: str) -> int:
    try:
        client = _client()

        keys = list(
            client.scan_iter(
                match=pattern,
                count=100,
            )
        )

        if keys:
            return client.delete(*keys)

        return 0

    except Exception as e:
        logger.warning(
            "Cache invalidate_pattern failed: %s",
            e,
        )

        return 0


def get_evaluation(
    resume_id: int,
    job_id: int,
) -> dict | None:
    return get(_eval_key(resume_id, job_id))


def set_evaluation(
    resume_id: int,
    job_id: int,
    payload: dict,
) -> None:
    set(
        _eval_key(resume_id, job_id),
        payload,
        REDIS.evaluation_ttl,
    )

    logger.debug(
        "Cached evaluation resume=%s job=%s ttl=%ss",
        resume_id,
        job_id,
        REDIS.evaluation_ttl,
    )


def get_resume_meta(resume_id: int) -> dict | None:
    return get(_resume_key(resume_id))


def set_resume_meta(
    resume_id: int,
    payload: dict,
) -> None:
    set(
        _resume_key(resume_id),
        payload,
        REDIS.resume_meta_ttl,
    )


def set_task_status(
    task_id: str,
    status: str,
    result: dict | None = None,
) -> None:
    payload = {"status": status}

    if result:
        payload["result"] = result

    set(
        _task_key(task_id),
        payload,
        ttl=60 * 60 * 2,
    )


def get_task_status(task_id: str) -> dict | None:
    return get(_task_key(task_id))


def make_content_hash(text: str) -> str:
    return hashlib.sha256(
        text.encode()
    ).hexdigest()