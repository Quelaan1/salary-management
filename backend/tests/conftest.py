import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import get_session, make_engine
from app.models import prepare_database

PASSWORD = "test-password"

os.environ["HR_PASSWORD"] = PASSWORD
os.environ["SESSION_SECRET"] = "test-secret"


@pytest.fixture
def password():
    return PASSWORD


@pytest.fixture
def session():
    engine = make_engine("sqlite://", poolclass=StaticPool)
    prepare_database(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
def visitor(session):
    """A client that has not signed in."""
    from app.main import app

    app.dependency_overrides[get_session] = lambda: session
    # HTTPS, because the session cookie is marked secure.
    yield TestClient(app, base_url="https://testserver")
    app.dependency_overrides.clear()


@pytest.fixture
def client(visitor):
    """A client signed in as the HR manager."""
    visitor.post("/api/login", json={"password": PASSWORD})
    return visitor
