from __future__ import annotations

from flask import (
    Blueprint,
    request,
    jsonify,
    g,
)

from pydantic import (
    ValidationError as PydanticValidationError,
)

from.validators.schemas import (
    EvaluationRequest,
)

from.services.evaluation_orchestrator import (
    EvaluationOrchestrator,
)

from.workers.tasks import (
    get_task_result,
)

from.utils.errors import (
    ValidationError,
)

from.utils.logger import (
    get_logger,
)

logger = get_logger(__name__)

evaluation_bp = Blueprint(
    "evaluation",
    __name__,
    url_prefix="/evaluation",
)

_orchestrator = (
    EvaluationOrchestrator()
)


@evaluation_bp.post("/")
def submit_evaluation():

    body = request.get_json(
        silent=True
    )

    if not body:
        raise ValidationError(
            "Request body must be JSON."
        )

    try:
        payload = (
            EvaluationRequest.model_validate(
                body
            )
        )

    except (
        PydanticValidationError
    ) as exc:

        raise ValidationError(
            "Invalid request.",
            {"fields": exc.errors()},
        )

    user_id: int | None = getattr(
        g,
        "user_id",
        None,
    )

    result = _orchestrator.submit(
        resume_id=payload.resume_id,
        job_id=payload.job_id,
        user_id=user_id,
    )

    status_code = (
        200
        if result.get("total_score")
        is not None
        else 202
    )

    return (
        jsonify(result),
        status_code,
    )


@evaluation_bp.get("/<int:eval_id>")
def get_evaluation(
    eval_id: int,
):

    user_id: int | None = getattr(
        g,
        "user_id",
        None,
    )

    result = _orchestrator.get(
        eval_id,
        requesting_user_id=user_id,
    )

    return jsonify(result), 200


@evaluation_bp.get("/task/<task_id>")
def poll_task(task_id: str):

    result = get_task_result(
        task_id
    )

    return jsonify(result), 200