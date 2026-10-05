import pytest


def person(**overrides) -> dict:
    fields = {
        "full_name": "Asha Rao",
        "email": "asha.rao@acme.example",
        "country": "India",
        "department": "Engineering",
        "job_title": "Software Engineer",
        "hire_date": "2022-04-01",
        "salary": "2400000.00",
    }
    return fields | overrides


def add(client, **overrides) -> dict:
    response = client.post("/api/employees", json=person(**overrides))
    assert response.status_code == 201, response.text
    return response.json()


def names(response) -> list[str]:
    return [item["full_name"] for item in response.json()["items"]]


@pytest.fixture
def three_people(client):
    add(client, full_name="Asha Rao", email="asha@acme.example", hire_date="2022-04-01")
    add(
        client,
        full_name="Ben Carter",
        email="ben@acme.example",
        country="United Kingdom",
        department="Finance",
        job_title="Accountant",
        hire_date="2019-09-15",
    )
    add(
        client,
        full_name="Chloe Meyer",
        email="chloe@acme.example",
        country="Germany",
        department="Engineering",
        job_title="Engineering Manager",
        hire_date="2024-01-08",
    )


def test_visitor_cannot_read_employees(visitor):
    assert visitor.get("/api/employees").status_code == 401


def test_new_employee_gets_a_number_and_the_currency_of_their_country(client):
    created = add(client, country="Germany")

    assert created["employee_number"] == "E00001"
    assert created["currency"] == "EUR"
    assert created["status"] == "active"
    assert created["salary"] == "2400000"


def test_new_employee_starts_their_salary_timeline(client):
    created = add(client)

    detail = client.get(f"/api/employees/{created['id']}").json()

    assert detail["salary_changes"] == [
        {
            "id": 1,
            "old_salary": None,
            "new_salary": "2400000",
            "effective_date": "2022-04-01",
            "reason": "Starting salary",
        }
    ]


@pytest.mark.parametrize(
    "bad",
    [
        {"country": "Atlantis"},
        {"email": "not-an-email"},
        {"salary": "0"},
        {"salary": "-10"},
        {"salary": "100.123"},
        {"full_name": "   "},
        {"hire_date": "yesterday"},
    ],
)
def test_bad_input_is_rejected(client, bad):
    assert client.post("/api/employees", json=person(**bad)).status_code == 422


def test_two_employees_cannot_share_an_email(client):
    add(client, email="asha@acme.example")

    response = client.post("/api/employees", json=person(email="ASHA@acme.example"))

    assert response.status_code == 409


def test_list_returns_one_page_and_the_full_count(client, three_people):
    first = client.get("/api/employees", params={"page_size": 2})
    second = client.get("/api/employees", params={"page_size": 2, "page": 2})

    assert names(first) == ["Asha Rao", "Ben Carter"]
    assert names(second) == ["Chloe Meyer"]
    assert first.json()["total"] == 3


def test_page_size_has_a_ceiling(client):
    assert client.get("/api/employees", params={"page_size": 101}).status_code == 422


@pytest.mark.parametrize(
    ("search", "found"),
    [
        ("carter", ["Ben Carter"]),
        ("CHLOE@", ["Chloe Meyer"]),
        ("a", ["Asha Rao", "Ben Carter", "Chloe Meyer"]),
        ("%", []),
        ("nobody", []),
    ],
)
def test_search_matches_name_or_email_ignoring_case(client, three_people, search, found):
    assert names(client.get("/api/employees", params={"search": search})) == found


@pytest.mark.parametrize(
    ("filters", "found"),
    [
        ({"country": "Germany"}, ["Chloe Meyer"]),
        ({"department": "Engineering"}, ["Asha Rao", "Chloe Meyer"]),
        ({"job_title": "Accountant"}, ["Ben Carter"]),
        ({"department": "Engineering", "country": "India"}, ["Asha Rao"]),
        ({"status": "left"}, []),
    ],
)
def test_filters_narrow_the_list(client, three_people, filters, found):
    assert names(client.get("/api/employees", params=filters)) == found


def test_list_sorts_by_name_unless_told_otherwise(client, three_people):
    newest_first = client.get("/api/employees", params={"sort": "-hire_date"})

    assert names(client.get("/api/employees")) == ["Asha Rao", "Ben Carter", "Chloe Meyer"]
    assert names(newest_first) == ["Chloe Meyer", "Asha Rao", "Ben Carter"]


def test_edit_changes_only_the_fields_sent(client):
    created = add(client)

    response = client.patch(
        f"/api/employees/{created['id']}",
        json={"job_title": "Senior Software Engineer", "full_name": None},
    )

    assert response.status_code == 200
    assert response.json() == created | {"job_title": "Senior Software Engineer"}


def test_employee_can_be_marked_as_left(client):
    created = add(client)

    client.patch(f"/api/employees/{created['id']}", json={"status": "left"})

    assert names(client.get("/api/employees", params={"status": "left"})) == ["Asha Rao"]


def test_edit_cannot_take_another_employees_email(client):
    add(client, email="asha@acme.example")
    ben = add(client, email="ben@acme.example")

    response = client.patch(f"/api/employees/{ben['id']}", json={"email": "asha@acme.example"})

    assert response.status_code == 409


def test_unknown_employee_is_not_found(client):
    assert client.get("/api/employees/999").status_code == 404
    assert client.patch("/api/employees/999", json={"status": "left"}).status_code == 404
