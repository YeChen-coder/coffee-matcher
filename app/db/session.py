from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings


settings = get_settings()
_engine = create_engine(
    settings.database_url,
    echo=settings.echo_sql,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create the database tables."""
    SQLModel.metadata.create_all(_engine)


def get_session() -> Iterator[Session]:
    with Session(_engine) as session:
        yield session


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    with Session(_engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
