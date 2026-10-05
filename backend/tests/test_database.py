from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.countries import COUNTRIES, RATES
from app.models import Employee, ExchangeRate, prepare_database


def employee(**overrides) -> Employee:
    fields = {
        "full_name": "Asha Rao",
        "email": "asha.rao@acme.example",
        "country": "India",
        "department": "Engineering",
        "job_title": "Software Engineer",
        "hire_date": date(2022, 4, 1),
        "salary_minor": 2_400_000_00,
        "currency": "INR",
    }
    return Employee(**(fields | overrides))


def test_rate_table_matches_the_country_list(session):
    rows = {rate.currency: rate.per_usd for rate in session.scalars(select(ExchangeRate))}

    assert rows == {currency: float(per_usd) for currency, per_usd in RATES.items()}


def test_every_country_has_a_rate():
    assert {currency for currency, _ in COUNTRIES.values()} == set(RATES)


def test_preparing_the_database_twice_changes_nothing(session):
    prepare_database(session.get_bind())

    assert len(session.scalars(select(ExchangeRate)).all()) == len(RATES)


def test_employee_number_comes_from_the_id(session):
    person = employee()
    session.add(person)
    session.commit()

    assert person.employee_number == "E00001"


def test_salary_must_be_above_zero(session):
    session.add(employee(salary_minor=0))

    with pytest.raises(IntegrityError):
        session.commit()


def test_currency_must_have_a_rate(session):
    session.add(employee(currency="XXX"))

    with pytest.raises(IntegrityError):
        session.commit()


def test_status_is_active_or_left(session):
    session.add(employee(status="retired"))

    with pytest.raises(IntegrityError):
        session.commit()
