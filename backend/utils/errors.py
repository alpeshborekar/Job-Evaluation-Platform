from __future__ import annotations
from http import HTTPStatus

from flask import Flask, jsonify

from utils.logger import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """
    Base class.
    Carries an HTTP status code
    and machine-readable code.
    """

    status_code: int = (
        HTTPStatus.INTERNAL_SERVER_ERROR
    )

    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        details: dict | None = None,
    ):
        super().__init__(message)

        self.message = message

        self.details = details or {}

    def to_dict(self) -> dict:
        payload: dict = {
            "error": self.error_code,
            "message": self.message,
        }

        if self.details:
            payload["details"] = self.details

        return payload


class ValidationError(AppError):
    status_code = (
        HTTPStatus.UNPROCESSABLE_ENTITY
    )

    error_code = "VALIDATION_ERROR"


class NotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND

    error_code = "NOT_FOUND"


class ConflictError(AppError):
    status_code = HTTPStatus.CONFLICT

    error_code = "CONFLICT"


class AuthenticationError(AppError):
    status_code = HTTPStatus.UNAUTHORIZED

    error_code = "UNAUTHENTICATED"


class AuthorizationError(AppError):
    status_code = HTTPStatus.FORBIDDEN

    error_code = "FORBIDDEN"


class UnsupportedFileTypeError(
    ValidationError
):
    error_code = (
        "UNSUPPORTED_FILE_TYPE"
    )


class FileTooLargeError(
    ValidationError
):
    error_code = "FILE_TOO_LARGE"


class ExternalServiceError(AppError):
    status_code = HTTPStatus.BAD_GATEWAY

    error_code = (
        "EXTERNAL_SERVICE_ERROR"
    )


class ProcessingError(AppError):
    status_code = (
        HTTPStatus.INTERNAL_SERVER_ERROR
    )

    error_code = "PROCESSING_ERROR"


def register_error_handlers(
    app: Flask,
) -> None:

    @app.errorhandler(AppError)
    def handle_app_error(
        exc: AppError,
    ):
        logger.warning(
            "AppError [%s] %s – %s",
            exc.status_code,
            exc.error_code,
            exc.message,
        )

        return (
            jsonify(exc.to_dict()),
            exc.status_code,
        )

    @app.errorhandler(404)
    def handle_404(_):
        return (
            jsonify(
                {
                    "error": "NOT_FOUND",
                    "message": (
                        "Route not found"
                    ),
                }
            ),
            404,
        )

    @app.errorhandler(405)
    def handle_405(_):
        return (
            jsonify(
                {
                    "error": (
                        "METHOD_NOT_ALLOWED"
                    ),
                    "message": (
                        "Method not allowed"
                    ),
                }
            ),
            405,
        )

    @app.errorhandler(Exception)
    def handle_unexpected(
        exc: Exception,
    ):
        logger.exception(
            "Unhandled exception: %s",
            exc,
        )

        return (
            jsonify(
                {
                    "error": (
                        "INTERNAL_ERROR"
                    ),
                    "message": (
                        "An unexpected error occurred."
                    ),
                }
            ),
            500,
        )