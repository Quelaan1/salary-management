import os
from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


def make_engine(url: str, **options) -> Engine:
    engine = create_engine(url, connect_args={"check_same_thread": False}, **options)

    # SQLite ignores foreign keys unless each connection turns them on.
    @event.listens_for(engine, "connect")
    def enforce_foreign_keys(connection, _record):
        connection.execute("PRAGMA foreign_keys = ON")

    return engine


engine = make_engine(os.environ.get("DATABASE_URL", "sqlite:///salary.db"))


def get_session() -> Iterator[Session]:
    with Session(engine, expire_on_commit=False) as session:
        yield session
