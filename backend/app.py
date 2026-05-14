from __future__ import annotations

from datetime import timedelta

from flask import Flask, jsonify
from flask_cors import CORS

from config.settings import APP
from utils.logger import (
    configure_logging,
    get_logger,
)
from utils.database import init_db
from utils.errors import (
    register_error_handlers,
)

logger = get_logger(__name__)


def create_app() -> Flask:
    configure_logging(
        level=APP.log_level,
        log_file=APP.log_file,
    )

    app = Flask(__name__)

    app.secret_key = APP.secret_key

    app.permanent_session_lifetime = timedelta(
        hours=2
    )

    CORS(
        app,
        supports_credentials=True,
    )

    init_db()

    from controllers.auth_controller import (
        auth_bp,
    )

    from controllers.resume_controller import (
        resume_bp,
    )

    from controllers.evaluation_controller import (
        evaluation_bp,
    )

    from controllers.job_controller import (
        job_bp,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(job_bp)

    register_error_handlers(app)

    @app.get("/health")
    def health():
        return (
            jsonify(
                {
                    "status": "ok",
                    "version": "2.0.0",
                }
            ),
            200,
        )

    logger.info(
        "Flask app created (debug=%s)",
        APP.debug,
    )

    return app