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
    RegisterRequest,
    LoginRequest,
    ChangePasswordRequest,
)

from services.auth_service import (
    AuthService,
)

from utils.auth import (
    login_required,
    set_session,
    clear_session,
)

from utils.errors import (
    ValidationError,
)

from utils.logger import (
    get_logger,
)

logger = get_logger(__name__)

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)

_svc = AuthService()


@auth_bp.post("/register")
def register():
    body = request.get_json(
        silent=True
    )

    if not body:
        raise ValidationError(
            "Request body must be JSON."
        )

    try:
        payload = (
            RegisterRequest.model_validate(
                body
            )
        )

    except PydanticError as exc:
        raise ValidationError(
            "Invalid registration data.",
            {"fields": exc.errors()},
        )

    user = _svc.register(
        username=payload.username,
        email=str(payload.email),
        password=payload.password,
    )

    return (
        jsonify(
            {
                "message": (
                    "Account created successfully."
                ),
                "user": user,
            }
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    body = request.get_json(
        silent=True
    )

    if not body:
        raise ValidationError(
            "Request body must be JSON."
        )

    try:
        payload = (
            LoginRequest.model_validate(
                body
            )
        )

    except PydanticError as exc:
        raise ValidationError(
            "Invalid login data.",
            {"fields": exc.errors()},
        )

    user = _svc.login(
        username=payload.username,
        password=payload.password,
    )

    set_session(
        user["id"],
        user["username"],
    )

    logger.info(
        "Session started user_id=%s",
        user["id"],
    )

    return (
        jsonify(
            {
                "message": (
                    "Login successful."
                ),
                "user": user,
            }
        ),
        200,
    )


@auth_bp.post("/logout")
def logout():
    clear_session()

    return (
        jsonify(
            {
                "message": (
                    "Logged out successfully."
                )
            }
        ),
        200,
    )


@auth_bp.get("/me")
@login_required
def me():
    return (
        jsonify(
            {
                "user_id": g.user_id,
                "username": g.username,
            }
        ),
        200,
    )


@auth_bp.post("/change-password")
@login_required
def change_password():
    body = request.get_json(
        silent=True
    )

    if not body:
        raise ValidationError(
            "Request body must be JSON."
        )

    try:
        payload = (
            ChangePasswordRequest.model_validate(
                body
            )
        )

    except PydanticError as exc:
        raise ValidationError(
            "Invalid data.",
            {"fields": exc.errors()},
        )

    _svc.change_password(
        g.user_id,
        old_password=(
            payload.old_password
        ),
        new_password=(
            payload.new_password
        ),
    )

    return (
        jsonify(
            {
                "message": (
                    "Password updated successfully."
                )
            }
        ),
        200,
    )