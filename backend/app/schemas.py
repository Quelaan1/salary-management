from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
)

from app.countries import COUNTRIES


def known_country(value: str) -> str:
    if value not in COUNTRIES:
        raise ValueError("Unknown country")
    return value


Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Label = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
Email = Annotated[EmailStr, AfterValidator(str.lower)]
Country = Annotated[str, AfterValidator(known_country)]
Money = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
Status = Literal["active", "left"]


class EmployeeIn(BaseModel):
    full_name: Name
    email: Email
    country: Country
    department: Label
    job_title: Label
    hire_date: date
    salary: Money


class EmployeeEdit(BaseModel):
    """Country and hire date stay fixed. A move changes currency and pay together."""

    full_name: Name | None = None
    email: Email | None = None
    department: Label | None = None
    job_title: Label | None = None
    status: Status | None = None


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_number: str
    full_name: str
    email: str
    country: str
    department: str
    job_title: str
    hire_date: date
    status: Status
    salary: Decimal
    currency: str


class SalaryChangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    old_salary: Decimal | None
    new_salary: Decimal
    effective_date: date
    reason: str


class EmployeeDetail(EmployeeOut):
    salary_changes: list[SalaryChangeOut]


class EmployeePage(BaseModel):
    items: list[EmployeeOut]
    total: int
