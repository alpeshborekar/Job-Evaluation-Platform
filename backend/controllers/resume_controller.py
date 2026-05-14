from __future__ import annotations

from flask import (
    Blueprint,
    request,
    jsonify,
    g,
)

from validators.schemas import (
    ResumeUploadMeta,
)

from services.resume_service import (
    ResumeService,
)

from workers.tasks import (
    get_task_result,
)

from utils.auth import (
    login_required,
)

from utils.errors import (
    ValidationError,
)

from utils.logger import (
    get_logger,
)

logger = get_logger(__name__)

resume_bp = Blueprint(
    "resume",
    __name__,
    url_prefix="/resume",
)

_svc = ResumeService()


@resume_bp.post("/upload")
@login_required
def upload_resume():

    if "resume" not in request.files:
        raise ValidationError(
            (
                "No file found. "
                "Send the file under "
                "the 'resume' field."
            )
        )

    file = request.files["resume"]

    if not file.filename:
        raise ValidationError(
            "Filename is empty."
        )

    meta = ResumeUploadMeta(
        email=request.form.get("email"),
        send_report=(
            request.form.get(
                "send_report",
                "false",
            ).lower()
            == "true"
        ),
    )

    user_id: int | None = getattr(
        g,
        "user_id",
        None,
    )

    result = _svc.upload(
        file,
        user_id=user_id,
        email=meta.email,
    )

    return jsonify(result), 202


@resume_bp.get("/<int:resume_id>")
@login_required
def get_resume(
    resume_id: int,
):
    user_id: int | None = getattr(
        g,
        "user_id",
        None,
    )

    result = _svc.get(
        resume_id,
        requesting_user_id=user_id,
    )

    return jsonify(result), 200


@resume_bp.get("/")
@login_required
def list_resumes():

    user_id: int | None = getattr(
        g,
        "user_id",
        None,
    )

    page = int(
        request.args.get(
            "page",
            1,
        )
    )

    per_page = min(
        int(
            request.args.get(
                "per_page",
                20,
            )
        ),
        100,
    )

    result = _svc.list_for_user(
        user_id,
        page=page,
        per_page=per_page,
    )

    return jsonify(result), 200


@resume_bp.get("/task/<task_id>")
def poll_task(task_id: str):

    result = get_task_result(
        task_id
    )

    return jsonify(result), 200