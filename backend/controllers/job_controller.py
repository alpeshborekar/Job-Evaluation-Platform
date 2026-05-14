from __future__ import annotations

from flask import (
    Blueprint,
    request,
    jsonify,
    g,
)

from pydantic import (
    ValidationError as PydanticError,
)

from validators.schemas import (
    JobCreateRequest,
    PaginationParams,
)

from services.job_service import (
    JobService,
)

from utils.auth import (
    login_required,
    optional_auth,
)

from utils.errors import (
    ValidationError,
)

from utils.logger import (
    get_logger,
)

logger = get_logger(__name__)

job_bp = Blueprint(
    "job",
    __name__,
    url_prefix="/job",
)

_svc = JobService()


@job_bp.post("/")
@login_required
def create_job():

    body = request.get_json(
        silent=True
    )

    if not body:
        raise ValidationError(
            "Request body must be JSON."
        )

    try:

        payload = (
            JobCreateRequest.model_validate(
                body
            )
        )

    except PydanticError as exc:

        raise ValidationError(
            "Invalid job data.",
            {"fields": exc.errors()},
        )

    job = _svc.create(
        title=payload.title,
        description=payload.description,
        company=payload.company,
        created_by=g.user_id,
    )

    return jsonify(job), 201


@job_bp.get("/")
@optional_auth
def list_jobs():

    try:

        params = PaginationParams(
            page=int(
                request.args.get(
                    "page",
                    1,
                )
            ),
            per_page=int(
                request.args.get(
                    "per_page",
                    20,
                )
            ),
        )

    except PydanticError as exc:

        raise ValidationError(
            (
                "Invalid pagination "
                "params."
            ),
            {"fields": exc.errors()},
        )

    result = _svc.list(
        page=params.page,
        per_page=params.per_page,
    )

    return jsonify(result), 200


@job_bp.get("/<int:job_id>")
@optional_auth
def get_job(job_id: int):

    job = _svc.get(job_id)

    return jsonify(job), 200


@job_bp.delete("/<int:job_id>")
@login_required
def delete_job(job_id: int):

    _svc.delete(
        job_id,
        requesting_user_id=g.user_id,
    )

    return jsonify(
        {
            "message": (
                f"Job {job_id} deleted."
            )
        }
    ), 200