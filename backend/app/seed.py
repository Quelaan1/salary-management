"""Fill an empty database with made-up employees.

    uv run python -m app.seed            # 10,000 employees
    uv run python -m app.seed --reset    # delete everyone and seed again

The random generator starts from a fixed number, so each run creates the same people.
"""

import argparse
import random
import re
import unicodedata
from datetime import date, timedelta

from faker import Faker
from sqlalchemy import delete, func, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.countries import COUNTRIES
from app.models import Employee, SalaryChange, prepare_database
from app.money import MINOR_UNITS

FIRST_HIRE = date(2012, 1, 2)
LAST_DAY = date(2026, 9, 30)

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

# country -> (share of headcount, pay compared with the United States, locale for names)
COUNTRY_MIX = {
    "India": (0.35, 0.3, "en_IN"),
    "United States": (0.25, 1.0, "en_US"),
    "United Kingdom": (0.10, 0.8, "en_GB"),
    "Germany": (0.08, 0.8, "de_DE"),
    "Brazil": (0.07, 0.4, "pt_BR"),
    "Canada": (0.06, 0.8, "en_CA"),
    "Australia": (0.05, 0.85, "en_AU"),
    "Singapore": (0.04, 0.8, "en_MS"),
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
    names = name_makers()
    employees, changes = [], []
    for employee_id in range(1, count + 1):
        employee, history = make_employee(rng, names, employee_id)
        employees.append(employee)
        changes.extend(history)

    session.execute(insert(Employee), employees)
    session.execute(insert(SalaryChange), changes)
    session.commit()


def name_makers() -> dict[str, Faker]:
    """One name generator per country, each started from its own fixed number."""
    makers = {}
    for number, (country, (_, _, locale)) in enumerate(COUNTRY_MIX.items()):
        makers[country] = Faker(locale)
        makers[country].seed_instance(number)
    return makers


def make_employee(
    rng: random.Random, names: dict[str, Faker], employee_id: int
) -> tuple[dict, list[dict]]:
    country = pick(rng, {name: mix[0] for name, mix in COUNTRY_MIX.items()})
    first, last = names[country].first_name(), names[country].last_name()
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
        "email": f"{email_name(first)}.{email_name(last)}{employee_id}@acme.example",
        "country": country,
        "department": department,
        "job_title": DEPARTMENTS[department][2][level],
        "hire_date": hire_date,
        "status": "left" if rng.random() < 0.06 else "active",
        "salary_minor": salary * MINOR_UNITS,
        "currency": currency,
    }
    return employee, history


def email_name(name: str) -> str:
    """Plain lowercase letters only: 'João' becomes 'joao', "O'Brien" becomes 'obrien'."""
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", plain.lower())


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
