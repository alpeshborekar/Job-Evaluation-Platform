from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import (
    session,
    g,
    jsonify,
)

from backend.utils.errors import (
    AuthenticationError,
    AuthorizationError,
)

from backend.utils.logger import (
    get_logger,
)

logger = get_logger(__name__)

_SESSION_USER_ID = "user_id"

_SESSION_USERNAME = "username"


def login_required(
    f: Callable,
) -> Callable:

    @wraps(f)
    def decorated(
        *args,
        **kwargs,
    ):
        user_id = session.get(
            _SESSION_USER_ID
        )

        if not user_id:
            return (
                jsonify(
                    {
                        "error": (
                            "UNAUTHENTICATED"
                        ),
                        "message": (
                            "Authentication required. "
                            "Please log in."
                        ),
                    }
                ),
                401,
            )

        g.user_id = user_id

        g.username = session.get(
            _SESSION_USERNAME,
            "",
        )

        return f(
            *args,
            **kwargs,
        )

    return decorated


def optional_auth(
    f: Callable,
) -> Callable:

    @wraps(f)
    def decorated(
        *args,
        **kwargs,
    ):
        g.user_id = session.get(
            _SESSION_USER_ID
        )

        g.username = session.get(
            _SESSION_USERNAME,
            "",
        )

        return f(
            *args,
            **kwargs,
        )

    return decorated


def set_session(
    user_id: int,
    username: str,
) -> None:

    session.permanent = True

    session[
        _SESSION_USER_ID
    ] = user_id

    session[
        _SESSION_USERNAME
    ] = username


def clear_session() -> None:
    session.clear()


def current_user_id() -> int | None:
    return session.get(
        _SESSION_USER_ID
    )