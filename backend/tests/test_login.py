def test_right_password_signs_in(visitor, password):
    response = visitor.post("/api/login", json={"password": password})

    assert response.status_code == 204
    assert visitor.get("/api/session").status_code == 204


def test_wrong_password_is_refused(visitor):
    response = visitor.post("/api/login", json={"password": "guess"})

    assert response.status_code == 401
    assert visitor.get("/api/session").status_code == 401


def test_visitor_is_not_signed_in(visitor):
    assert visitor.get("/api/session").status_code == 401


def test_logout_ends_the_session(client):
    client.post("/api/logout")

    assert client.get("/api/session").status_code == 401


def test_session_cookie_is_hidden_from_scripts_and_https_only(visitor, password):
    response = visitor.post("/api/login", json={"password": password})

    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "secure" in cookie
    assert "samesite=lax" in cookie
