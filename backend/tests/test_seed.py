from itertools import pairwise

import pytest
from sqlalchemy import func, select

from app.countries import COUNTRIES
from app.models import Employee
from app.seed import COUNTRY_MIX, seed


def people(session) -> list[tuple]:
    rows = session.scalars(select(Employee).order_by(Employee.id))
    return [
        (row.full_name, row.email, row.country, row.job_title, row.hire_date, row.salary_minor)
        for row in rows
    ]


def count(session) -> int:
    return session.scalar(select(func.count()).select_from(Employee))


def test_seed_covers_every_country():
    assert set(COUNTRY_MIX) == set(COUNTRIES)


def test_seed_creates_10000_employees_by_default(session):
    seed(session)

    assert count(session) == 10_000


def test_each_run_creates_the_same_people(session, other_session):
    seed(session, 200)
    seed(other_session, 200)

    assert people(session) == people(other_session)


def test_everyone_is_paid_in_the_currency_of_their_country(session):
    seed(session, 200)

    for employee in session.scalars(select(Employee)):
        assert employee.currency == COUNTRIES[employee.country][0]


def test_each_timeline_runs_from_the_starting_salary_to_the_current_one(session):
    seed(session, 200)

    for employee in session.scalars(select(Employee)):
        timeline = employee.salary_changes
        assert timeline[0].old_salary_minor is None
        assert timeline[0].effective_date == employee.hire_date
        assert timeline[-1].new_salary_minor == employee.salary_minor
        for earlier, later in pairwise(timeline):
            assert later.old_salary_minor == earlier.new_salary_minor
            assert later.effective_date >= earlier.effective_date


def test_seed_refuses_a_database_that_has_employees(session):
    seed(session, 5)

    with pytest.raises(ValueError, match="already has employees"):
        seed(session, 5)


def test_reset_replaces_everyone(session):
    seed(session, 5)

    seed(session, 8, reset=True)

    assert count(session) == 8
