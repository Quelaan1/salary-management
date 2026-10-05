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
