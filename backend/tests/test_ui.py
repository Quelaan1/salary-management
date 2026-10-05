import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.ui import UiFiles


@pytest.fixture
def site(tmp_path):
    (tmp_path / "index.html").write_text("<p>the app</p>")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text("console.log('hi')")
    app = FastAPI()
    app.mount("/", UiFiles(directory=tmp_path, html=True))
    return TestClient(app)


def test_files_are_served(site):
    assert site.get("/").text == "<p>the app</p>"
    assert site.get("/assets/app.js").text == "console.log('hi')"


def test_page_address_gets_the_app(site):
    response = site.get("/people/7")

    assert response.status_code == 200
    assert response.text == "<p>the app</p>"


def test_unknown_api_path_is_still_not_found(site):
    assert site.get("/api/nope").status_code == 404
