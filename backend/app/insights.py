from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, literal, select
from sqlalchemy.orm import Session

from app.auth import require_login
from app.countries import COUNTRIES
from app.db import get_session
from app.models import Employee, ExchangeRate
from app.money import to_major

router = APIRouter(prefix="/api", dependencies=[Depends(require_login)])

Db = Annotated[Session, Depends(get_session)]

SPLITS = {
    "country": Employee.country,
    "department": Employee.department,
    "job_title": Employee.job_title,
}


class Group(BaseModel):
    name: str
    headcount: int
    total: Decimal
    lowest: Decimal
    median: Decimal
    average: Decimal
    highest: Decimal


class Insights(BaseModel):
    currency: str = "USD"
    groups: list[Group]


class CountryOut(BaseModel):
    name: str
    currency: str


class Filters(BaseModel):
    countries: list[CountryOut]
    departments: list[str]
    job_titles: list[str]


@router.get("/insights")
def insights(db: Db, by: Literal["country", "department", "job_title"] | None = None) -> Insights:
    """Pay of current employees in USD, for the company or split into groups."""
    name = SPLITS[by] if by else literal("Company")
    # One row per current employee: their group and annual pay in USD cents.
    pay = (
        select(
            name.label("name"),
            func.round(Employee.salary_minor / ExchangeRate.per_usd).label("usd"),
        )
        .join(ExchangeRate, ExchangeRate.currency == Employee.currency)
        .where(Employee.status == "active")
        .subquery()
    )
    # SQLite's median() needs a build option that is off by default. Rank the
    # rows of each group and average the middle one or two.
    ranked = select(
        pay.c.name,
        pay.c.usd,
        func.row_number().over(partition_by=pay.c.name, order_by=pay.c.usd).label("position"),
        func.count().over(partition_by=pay.c.name).label("size"),
    ).subquery()
    medians = (
        select(ranked.c.name, func.avg(ranked.c.usd).label("median"))
        .where(ranked.c.position.between((ranked.c.size + 1) // 2, (ranked.c.size + 2) // 2))
        .group_by(ranked.c.name)
        .subquery()
    )
    rows = db.execute(
        select(
            pay.c.name,
            func.count(),
            func.sum(pay.c.usd),
            func.min(pay.c.usd),
            medians.c.median,
            func.avg(pay.c.usd),
            func.max(pay.c.usd),
        )
        .join(medians, medians.c.name == pay.c.name)
        .group_by(pay.c.name)
        .order_by(pay.c.name)
    )
    return Insights(
        groups=[
            Group(
                name=name,
                headcount=headcount,
                total=to_major(total),
                lowest=to_major(lowest),
                median=to_major(median),
                average=to_major(average),
                highest=to_major(highest),
            )
            for name, headcount, total, lowest, median, average, highest in rows
        ]
    )


@router.get("/filters")
def filters(db: Db) -> Filters:
    def used(column) -> list[str]:
        return list(db.scalars(select(column).distinct().order_by(column)))

    return Filters(
        countries=[
            CountryOut(name=name, currency=currency) for name, (currency, _) in COUNTRIES.items()
        ],
        departments=used(Employee.department),
        job_titles=used(Employee.job_title),
    )
