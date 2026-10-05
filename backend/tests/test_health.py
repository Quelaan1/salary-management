def test_health_reports_ok_without_signing_in(visitor):
    response = visitor.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
