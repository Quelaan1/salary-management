from datetime import date, timedelta

import pytest

from tests.helpers import add


@pytest.fixture
def asha(client) -> dict:
    return add(client, hire_date="2022-04-01", salary="2400000.00")


def change(client, employee, **overrides):
    body = {"salary": "2700000.00", "effective_date": "2023-04-01", "reason": "Annual review"}
    return client.post(f"/api/employees/{employee['id']}/salary", json=body | overrides)


def test_change_updates_the_current_salary(client, asha):
    response = change(client, asha)

    assert response.status_code == 201
    assert response.json()["salary"] == "2700000"


def test_timeline_keeps_each_change_oldest_first(client, asha):
    change(client, asha)
    change(client, asha, salary="3100000.00", effective_date="2024-04-01", reason="Promotion")

    timeline = client.get(f"/api/employees/{asha['id']}").json()["salary_changes"]

    assert [(row["old_salary"], row["new_salary"], row["reason"]) for row in timeline] == [
        (None, "2400000", "Starting salary"),
        ("2400000", "2700000", "Annual review"),
        ("2700000", "3100000", "Promotion"),
    ]


def test_same_amount_is_not_a_change(client, asha):
    assert change(client, asha, salary="2400000.00").status_code == 409


def test_date_cannot_be_in_the_future(client, asha):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    assert change(client, asha, effective_date=tomorrow).status_code == 422


def test_date_cannot_be_before_the_last_change(client, asha):
    response = change(client, asha, effective_date="2022-03-31")

    assert response.status_code == 422
    assert "2022-04-01" in response.json()["detail"]


def test_someone_who_left_cannot_get_a_new_salary(client, asha):
    client.patch(f"/api/employees/{asha['id']}", json={"status": "left"})

    assert change(client, asha).status_code == 409


@pytest.mark.parametrize("bad", [{"salary": "0"}, {"reason": "  "}, {"effective_date": "soon"}])
def test_bad_input_is_rejected(client, asha, bad):
    assert change(client, asha, **bad).status_code == 422


def test_unknown_employee_is_not_found(client):
    assert change(client, {"id": 999}).status_code == 404
