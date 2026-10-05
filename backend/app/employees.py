from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import require_login
from app.countries import COUNTRIES
from app.db import get_session
from app.models import Employee, SalaryChange
from app.money import to_minor
from app.schemas import (
    EmployeeDetail,
    EmployeeEdit,
    EmployeeIn,
    EmployeeOut,
    EmployeePage,
    SalaryChangeIn,
    Status,
)

router = APIRouter(prefix="/api/employees", dependencies=[Depends(require_login)])

Db = Annotated[Session, Depends(get_session)]

SORTS = {"name": Employee.full_name, "hire_date": Employee.hire_date}


def find(db: Session, employee_id: int) -> Employee:
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(404, "No such employee")
    return employee


def save(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Another employee already has that email") from None


@router.get("")
def list_employees(
    db: Db,
    search: str = "",
    country: str = "",
    department: str = "",
    job_title: str = "",
    status: Status | None = None,
    sort: Literal["name", "-name", "hire_date", "-hire_date"] = "name",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
) -> EmployeePage:
    query = select(Employee)
    if search := search.strip():
        query = query.where(
            or_(
                Employee.full_name.icontains(search, autoescape=True),
                Employee.email.icontains(search, autoescape=True),
            )
        )
    filters = {
        Employee.country: country,
        Employee.department: department,
        Employee.job_title: job_title,
        Employee.status: status,
    }
    for column, value in filters.items():
        if value:
            query = query.where(column == value)

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    column = SORTS[sort.removeprefix("-")]
    order = column.desc() if sort.startswith("-") else column.asc()
    rows = db.scalars(
        query.order_by(order, Employee.id).limit(page_size).offset((page - 1) * page_size)
    )
    return EmployeePage(items=rows.all(), total=total)


@router.post("", status_code=201)
def add_employee(body: EmployeeIn, db: Db) -> EmployeeOut:
    currency, _ = COUNTRIES[body.country]
    employee = Employee(
        **body.model_dump(exclude={"salary"}),
        salary_minor=to_minor(body.salary),
        currency=currency,
    )
    employee.salary_changes.append(
        SalaryChange(
            new_salary_minor=employee.salary_minor,
            effective_date=body.hire_date,
            reason="Starting salary",
        )
    )
    db.add(employee)
    save(db)
    return employee


@router.get("/{employee_id}")
def get_employee(employee_id: int, db: Db) -> EmployeeDetail:
    return find(db, employee_id)


@router.patch("/{employee_id}")
def edit_employee(employee_id: int, body: EmployeeEdit, db: Db) -> EmployeeOut:
    employee = find(db, employee_id)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(employee, field, value)
    save(db)
    return employee


@router.post("/{employee_id}/salary", status_code=201)
def change_salary(employee_id: int, body: SalaryChangeIn, db: Db) -> EmployeeDetail:
    employee = find(db, employee_id)
    new_salary = to_minor(body.salary)
    last_change = employee.salary_changes[-1].effective_date

    if employee.status != "active":
        raise HTTPException(409, "This person has left")
    if new_salary == employee.salary_minor:
        raise HTTPException(409, "That is already their salary")
    if body.effective_date > date.today():
        raise HTTPException(422, "The date cannot be in the future")
    if body.effective_date < last_change:
        raise HTTPException(422, f"The date cannot be before their last change on {last_change}")

    employee.salary_changes.append(
        SalaryChange(
            old_salary_minor=employee.salary_minor,
            new_salary_minor=new_salary,
            effective_date=body.effective_date,
            reason=body.reason,
        )
    )
    employee.salary_minor = new_salary
    db.commit()
    return employee
