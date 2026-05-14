from __future__ import annotations
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class _DatabaseConfig:

    host: str = os.getenv(
        "MYSQL_HOST",
        "localhost",
    )

    port: int = int(
        os.getenv(
            "MYSQL_PORT",
            3306,
        )
    )

    user: str = os.getenv(
        "MYSQL_USER",
        "root",
    )

    password: str = os.getenv(
        "MYSQL_PASSWORD",
        "",
    )

    db: str = os.getenv(
        "MYSQL_DB",
        "ai_resume",
    )

    pool_size: int = int(
        os.getenv(
            "DB_POOL_SIZE",
            10,
        )
    )

    pool_timeout: int = int(
        os.getenv(
            "DB_POOL_TIMEOUT",
            30,
        )
    )

    @property
    def url(self) -> str:

        database_url = os.getenv(
            "DATABASE_URL"
        )

        if database_url:

            database_url = database_url.replace(
                "mysql://",
                "mysql+pymysql://",
                1,
            )

            return database_url

        return (
            f"mysql+pymysql://"
            f"{self.user}:{self.password}"
            f"@{self.host}:{self.port}"
            f"/{self.db}?charset=utf8mb4"
        )


@dataclass(frozen=True)
class _RedisConfig:

    host: str = os.getenv(
        "REDIS_HOST",
        "localhost",
    )

    port: int = int(
        os.getenv(
            "REDIS_PORT",
            6379,
        )
    )

    db: int = int(
        os.getenv(
            "REDIS_DB",
            0,
        )
    )

    password: str | None = os.getenv(
        "REDIS_PASSWORD"
    )

    evaluation_ttl: int = (
        60 * 60 * 24
    )

    resume_meta_ttl: int = (
        60 * 60 * 6
    )

    session_ttl: int = (
        60 * 60 * 2
    )

    @property
    def url(self) -> str:

        auth = (
            f":{self.password}@"
            if self.password
            else ""
        )

        return (
            f"redis://"
            f"{auth}"
            f"{self.host}:"
            f"{self.port}/"
            f"{self.db}"
        )


@dataclass(frozen=True)
class _CeleryConfig:

    broker_url: str = field(
        default_factory=lambda:
        _RedisConfig().url
    )

    result_backend: str = field(
        default_factory=lambda:
        _RedisConfig().url
    )

    task_serializer: str = "json"

    result_serializer: str = "json"

    accept_content: tuple = (
        "json",
    )

    task_acks_late: bool = True

    task_reject_on_worker_lost: bool = True

    worker_prefetch_multiplier: int = 1


@dataclass(frozen=True)
class _GeminiConfig:

    api_key: str = os.getenv(
        "GEMINI_API_KEY",
        "",
    )

    model: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-1.5-flash",
    )

    max_tokens: int = 2048

    temperature: float = 0.3


@dataclass(frozen=True)
class _AppConfig:

    secret_key: str = os.getenv(
        "SECRET_KEY",
        "change-me-in-production",
    )

    debug: bool = (
        os.getenv(
            "FLASK_DEBUG",
            "false",
        ).lower()
        == "true"
    )

    upload_dir: str = os.getenv(
        "UPLOAD_DIR",
        "temp",
    )

    max_upload_mb: int = int(
        os.getenv(
            "MAX_UPLOAD_MB",
            10,
        )
    )

    log_level: str = os.getenv(
        "LOG_LEVEL",
        "INFO",
    )

    log_file: str = os.getenv(
        "LOG_FILE",
        "logs/app.log",
    )


DB = _DatabaseConfig()

REDIS = _RedisConfig()

CELERY = _CeleryConfig()

GEMINI = _GeminiConfig()

APP = _AppConfig()


SCORING_WEIGHTS: dict[
    str,
    float,
] = {
    "skills_match": 0.45,
    "experience_relevance": 0.30,
    "keyword_relevance": 0.25,
}


RECOMMENDATION_THRESHOLDS: dict[
    str,
    int,
] = {
    "hire": 75,
    "improve": 45,
}