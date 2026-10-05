import pytest
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import make_engine
from app.models import prepare_database


@pytest.fixture
def session():
    engine = make_engine("sqlite://", poolclass=StaticPool)
    prepare_database(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session
