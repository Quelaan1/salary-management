from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, String, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from app.countries import RATES
from app.money import to_major


class Base(DeclarativeBase):
    pass


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    currency: Mapped[str] = mapped_column(String(3), primary_key=True)
    per_usd: Mapped[float]


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("salary_minor > 0"),
        CheckConstraint("status IN ('active', 'left')"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), index=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    country: Mapped[str] = mapped_column(String(60), index=True)
    department: Mapped[str] = mapped_column(String(60), index=True)
    job_title: Mapped[str] = mapped_column(String(80), index=True)
    hire_date: Mapped[date]
    status: Mapped[str] = mapped_column(String(10), default="active", index=True)
    # Annual base pay in the smallest unit of the currency (cents, paise).
    salary_minor: Mapped[int]
    currency: Mapped[str] = mapped_column(ForeignKey("exchange_rates.currency"))

    salary_changes: Mapped[list[SalaryChange]] = relationship(
        order_by="SalaryChange.effective_date, SalaryChange.id"
    )

    @property
    def employee_number(self) -> str:
        return f"E{self.id:05d}"

    @property
    def salary(self) -> Decimal:
        return to_major(self.salary_minor)


class SalaryChange(Base):
    __tablename__ = "salary_changes"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    # Empty for the starting salary.
    old_salary_minor: Mapped[int | None]
    new_salary_minor: Mapped[int]
    effective_date: Mapped[date]
    reason: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    @property
    def old_salary(self) -> Decimal | None:
        return None if self.old_salary_minor is None else to_major(self.old_salary_minor)

    @property
    def new_salary(self) -> Decimal:
        return to_major(self.new_salary_minor)


def prepare_database(engine: Engine) -> None:
    """Create missing tables and copy the fixed rates into exchange_rates."""
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        for currency, per_usd in RATES.items():
            session.merge(ExchangeRate(currency=currency, per_usd=float(per_usd)))
        session.commit()
