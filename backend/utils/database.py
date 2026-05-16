from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from config.settings import DB
from models.orm import Base
from utils.logger import get_logger

logger = get_logger(__name__)

_engine = create_engine(
    DB.url,
    poolclass=QueuePool,

    # Connection pool settings
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,

    # Important fixes for Render/MySQL disconnects
    pool_pre_ping=True,
    pool_recycle=280,

    # Stability settings
    pool_reset_on_return="rollback",

    echo=False,
)


@event.listens_for(
    _engine,
    "before_cursor_execute",
)
def _before_execute(
    conn,
    cursor,
    statement,
    params,
    context,
    executemany,
):
    import time

    context._query_start_time = (
        time.time()
    )


@event.listens_for(
    _engine,
    "after_cursor_execute",
)
def _after_execute(
    conn,
    cursor,
    statement,
    params,
    context,
    executemany,
):
    import time

    elapsed = (
        time.time()
        - context._query_start_time
    )

    if elapsed > 0.5:
        logger.warning(
            "Slow query (%.2fs): %.120s",
            elapsed,
            statement,
        )


_SessionFactory = sessionmaker(
    bind=_engine,
    autocommit=False,
    autoflush=False,
)


def init_db() -> None:
    try:
        Base.metadata.create_all(
            bind=_engine
        )

        logger.info(
            "Database tables initialised."
        )

    except Exception as e:
        logger.error(
            "Database initialization failed: %s",
            str(e),
        )

        raise


@contextmanager
def db_session() -> Generator[
    Session,
    None,
    None,
]:
    session: Session = (
        _SessionFactory()
    )

    try:
        yield session

        session.commit()

    except Exception:
        session.rollback()

        raise

    finally:
        session.close()