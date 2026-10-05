"""Fill an empty database with made-up employees.

    uv run python -m app.seed            # 10,000 employees
    uv run python -m app.seed --reset    # delete everyone and seed again

The random generator starts from a fixed number, so each run creates the same people.
"""

import argparse
import random
from datetime import date, timedelta

from sqlalchemy import delete, func, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.countries import COUNTRIES
from app.models import Employee, SalaryChange, prepare_database
from app.money import MINOR_UNITS

FIRST_HIRE = date(2012, 1, 2)
LAST_DAY = date(2026, 9, 30)

FIRST_NAMES = """
Aarav Aditi Akira Alice Amara Ananya Andre Anna Arjun Beatriz Ben Camila Carlos Chloe
Daniel Diego Elena Emma Fatima Felix Gabriel Grace Hannah Hiro Imran Isabel Jack Kavya
Lars Leah Liam Lucas Mei Mia Mohan Nadia Noah Olivia Priya Rahul Rohan Sara Sofia Tariq
Thomas Vikram Wei Zoe
""".split()

LAST_NAMES = """
Almeida Bauer Bose Brown Carter Chen Costa Das Evans Fernandes Fischer Gupta Harris
Iyer Jones Kapoor Khan Kim Kumar Lee Lim Martin Mehta Meyer Nair Nguyen Oliveira Patel
Rao Reddy Santos Schmidt Sharma Silva Singh Smith Tan Taylor Thomas Verma Walker Wang
White Williams Wilson Wong Young Zhang
""".split()

# department -> (share of headcount, pay factor, job titles from junior to senior)
DEPARTMENTS = {
    "Engineering": (
        0.34,
        1.15,
        ["Software Engineer", "Senior Software Engineer", "Staff Engineer"],
    ),
    "Sales": (0.18, 1.0, ["Sales Representative", "Account Executive", "Sales Manager"]),
    "Customer Support": (
        0.16,
        0.75,
        ["Support Specialist", "Senior Support Specialist", "Support Lead"],
    ),
    "Operations": (
        0.10,
        0.85,
        ["Operations Analyst", "Senior Operations Analyst", "Operations Manager"],
    ),
    "Product": (0.08, 1.1, ["Product Analyst", "Product Manager", "Senior Product Manager"]),
    "Finance": (0.06, 0.95, ["Accountant", "Senior Accountant", "Finance Manager"]),
    "People": (0.05, 0.9, ["HR Generalist", "HR Business Partner", "HR Manager"]),
    "Design": (0.03, 1.0, ["Product Designer", "Senior Product Designer", "Design Lead"]),
}

# country -> (share of headcount, pay compared with the United States)
COUNTRY_MIX = {
    "India": (0.35, 0.3),
    "United States": (0.25, 1.0),
    "United Kingdom": (0.10, 0.8),
    "Germany": (0.08, 0.8),
    "Brazil": (0.07, 0.4),
    "Canada": (0.06, 0.8),
    "Australia": (0.05, 0.85),
    "Singapore": (0.04, 0.8),
}

# Annual pay in USD for a junior, mid and senior job, and how common each level is.
LEVEL_PAY = [60_000, 95_000, 140_000]
LEVEL_SHARE = [0.5, 0.35, 0.15]


def seed(session: Session, count: int = 10_000, *, reset: bool = False) -> None:
    if reset:
        session.execute(delete(SalaryChange))
        session.execute(delete(Employee))
    elif session.scalar(select(func.count()).select_from(Employee)):
        raise ValueError("The database already has employees. Use --reset to replace them.")

    rng = random.Random(42)
    employees, changes = [], []
    for employee_id in range(1, count + 1):
        employee, history = make_employee(rng, employee_id)
        employees.append(employee)
        changes.extend(history)

    session.execute(insert(Employee), employees)
    session.execute(insert(SalaryChange), changes)
    session.commit()


def make_employee(rng: random.Random, employee_id: int) -> tuple[dict, list[dict]]:
    first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
    country = pick(rng, {name: share for name, (share, _) in COUNTRY_MIX.items()})
    department = pick(rng, {name: share for name, (share, _, _) in DEPARTMENTS.items()})
    level = rng.choices(range(3), LEVEL_SHARE)[0]
    currency, per_usd = COUNTRIES[country]
    hire_date = FIRST_HIRE + timedelta(days=rng.randrange((LAST_DAY - FIRST_HIRE).days))

    usd = LEVEL_PAY[level] * DEPARTMENTS[department][1] * COUNTRY_MIX[country][1]
    salary = round_to_thousand(usd * float(per_usd) * rng.uniform(0.85, 1.2))

    history = [change(employee_id, None, salary, hire_date, "Starting salary")]
    for raise_date in raise_dates(rng, hire_date):
        raised = round_to_thousand(salary * rng.uniform(1.03, 1.12))
        if raised != salary:
            history.append(change(employee_id, salary, raised, raise_date, "Annual review"))
            salary = raised

    employee = {
        "id": employee_id,
        "full_name": f"{first} {last}",
        "email": f"{first}.{last}{employee_id}@acme.example".lower(),
        "country": country,
        "department": department,
        "job_title": DEPARTMENTS[department][2][level],
        "hire_date": hire_date,
        "status": "left" if rng.random() < 0.06 else "active",
        "salary_minor": salary * MINOR_UNITS,
        "currency": currency,
    }
    return employee, history


def pick(rng: random.Random, shares: dict[str, float]) -> str:
    return rng.choices(list(shares), list(shares.values()))[0]


def round_to_thousand(amount: float) -> int:
    return max(1000, round(amount / 1000) * 1000)


def raise_dates(rng: random.Random, hire_date: date) -> list[date]:
    """Up to three raises, about one every two years."""
    years = (LAST_DAY - hire_date).days // 365
    count = min(3, years // 2)
    span = (LAST_DAY - hire_date).days
    return sorted(hire_date + timedelta(days=rng.randrange(180, span)) for _ in range(count))


def change(employee_id: int, old: int | None, new: int, on: date, reason: str) -> dict:
    return {
        "employee_id": employee_id,
        "old_salary_minor": None if old is None else old * MINOR_UNITS,
        "new_salary_minor": new * MINOR_UNITS,
        "effective_date": on,
        "reason": reason,
    }


def seed_if_empty(engine: Engine) -> None:
    with Session(engine) as session:
        if not session.scalar(select(func.count()).select_from(Employee)):
            seed(session)


def main() -> None:
    from app.db import engine

    parser = argparse.ArgumentParser(description="Fill the database with made-up employees.")
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--reset", action="store_true", help="delete everyone first")
    args = parser.parse_args()

    prepare_database(engine)
    with Session(engine) as session:
        try:
            seed(session, args.count, reset=args.reset)
        except ValueError as error:
            raise SystemExit(str(error)) from None
    print(f"Seeded {args.count} employees.")


if __name__ == "__main__":
    main()
