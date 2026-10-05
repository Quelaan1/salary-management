import pytest

from tests.helpers import add


@pytest.fixture
def company(client):
    """Five current employees worth 10k, 20k, 70k, 100k and 150k USD, and one who left."""
    people = [
        ("India", "Engineering", "Software Engineer", "963000.00"),
        ("India", "Engineering", "Software Engineer", "1926000.00"),
        ("United States", "Engineering", "Staff Engineer", "150000.00"),
        ("United States", "Finance", "Accountant", "70000.00"),
        ("Germany", "Finance", "Accountant", "89254.00"),
        ("United States", "Finance", "Accountant", "999999.00"),
    ]
    for number, (country, department, job_title, salary) in enumerate(people):
        created = add(
            client,
            email=f"person{number}@acme.example",
            country=country,
            department=department,
            job_title=job_title,
            salary=salary,
        )
    client.patch(f"/api/employees/{created['id']}", json={"status": "left"})


def groups(client, by=None) -> dict[str, dict]:
    response = client.get("/api/insights", params={"by": by} if by else None)
    assert response.status_code == 200, response.text
    return {group.pop("name"): group for group in response.json()["groups"]}


def test_company_figures_are_in_usd_and_skip_people_who_left(client, company):
    response = client.get("/api/insights").json()

    assert response == {
        "currency": "USD",
        "groups": [
            {
                "name": "Company",
                "headcount": 5,
                "total": "350000",
                "lowest": "10000",
                "median": "70000",
                "average": "70000",
                "highest": "150000",
            }
        ],
    }


def test_split_by_country(client, company):
    by_country = groups(client, "country")

    assert list(by_country) == ["Germany", "India", "United States"]
    assert by_country["India"] == {
        "headcount": 2,
        "total": "30000",
        "lowest": "10000",
        "median": "15000",
        "average": "15000",
        "highest": "20000",
    }
    assert by_country["United States"]["headcount"] == 2
    assert by_country["United States"]["median"] == "110000"


def test_split_by_department(client, company):
    by_department = groups(client, "department")

    assert by_department["Engineering"]["median"] == "20000"
    assert by_department["Engineering"]["average"] == "60000"
    assert by_department["Finance"]["median"] == "85000"


def test_split_by_job_title(client, company):
    by_job = groups(client, "job_title")

    assert {name: group["headcount"] for name, group in by_job.items()} == {
        "Accountant": 2,
        "Software Engineer": 2,
        "Staff Engineer": 1,
    }


def test_unknown_split_is_rejected(client):
    assert client.get("/api/insights", params={"by": "salary"}).status_code == 422


def test_empty_company_has_no_groups(client):
    assert client.get("/api/insights").json()["groups"] == []


def test_visitor_cannot_read_insights(visitor):
    assert visitor.get("/api/insights").status_code == 401
    assert visitor.get("/api/filters").status_code == 401


def test_filters_list_every_country_and_the_values_in_use(client, company):
    filters = client.get("/api/filters").json()

    assert {"name": "India", "currency": "INR"} in filters["countries"]
    assert len(filters["countries"]) == 8
    assert filters["departments"] == ["Engineering", "Finance"]
    assert filters["job_titles"] == ["Accountant", "Software Engineer", "Staff Engineer"]
