from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.config import DATABASE_URL


def lower(text: str | None) -> str | None:
    return text if text is None else text.lower()


def make_engine(url: str, **options) -> Engine:
    engine = create_engine(url, connect_args={"check_same_thread": False}, **options)

    @event.listens_for(engine, "connect")
    def configure(connection, _record):
        # SQLite ignores foreign keys unless each connection turns them on.
        connection.execute("PRAGMA foreign_keys = ON")
        # SQLite's own lower() changes ASCII letters only, so a search for
        # "ângela" would miss "Ângela". Python's lower() knows every alphabet.
        connection.create_function("lower", 1, lower, deterministic=True)

    return engine


engine = make_engine(DATABASE_URL)


def get_session() -> Iterator[Session]:
    with Session(engine, expire_on_commit=False) as session:
        yield session
