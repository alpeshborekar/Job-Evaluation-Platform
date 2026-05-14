from __future__ import annotations
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from backend.config.settings import DB
from backend.models.orm import Base
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_engine = create_engine(
    DB.url,
    poolclass=QueuePool,
    pool_size=DB.pool_size,
    max_overflow=5,
    pool_timeout=DB.pool_timeout,
    pool_pre_ping=True,
    echo=False,
)


@event.listens_for(_engine, "after_cursor_execute")
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


@event.listens_for(_engine, "before_cursor_execute")
def _before_execute(
    conn,
    cursor,
    statement,
    params,
    context,
    executemany,
):
    import time

    context._query_start_time = time.time()


_SessionFactory = sessionmaker(
    bind=_engine,
    autocommit=False,
    autoflush=False,
)


def init_db() -> None:
    Base.metadata.create_all(bind=_engine)

    logger.info(
        "Database tables initialised."
    )


@contextmanager
def db_session() -> Generator[
    Session,
    None,
    None,
]:
    session: Session = _SessionFactory()

    try:
        yield session

        session.commit()

    except Exception:
        session.rollback()

        raise

    finally:
        session.close()