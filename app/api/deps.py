from typing import Iterator

from sqlmodel import Session

from app.db.session import get_session


def get_db() -> Iterator[Session]:
    yield from get_session()
