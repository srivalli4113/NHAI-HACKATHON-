from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Employee
from app.schemas.contracts import EmployeeOut, RegistrationResponse
from app.security.auth import AuthIdentity, get_current_identity, require_operator
from app.services.face_service import face_service

router = APIRouter(prefix="/employees", tags=["employees"])


def employee_out(employee: Employee) -> EmployeeOut:
    return EmployeeOut(
        employee_id=employee.employee_id,
        name=employee.name,
        department=employee.department,
        designation=employee.designation,
        created_at=employee.created_at,
        is_active=employee.is_active,
    )


@router.post("/register", response_model=RegistrationResponse)
async def register_employee(
    name: str = Form(...),
    employee_id: str = Form(...),
    department: str = Form(...),
    designation: str = Form(...),
    photograph: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: AuthIdentity = Depends(get_current_identity),
) -> RegistrationResponse:
    employee = await face_service.register(db, name, employee_id, department, designation, photograph, user.username)
    return RegistrationResponse(employee=employee_out(employee), quality_passed=True, quality_issues=[])


@router.get("", response_model=list[EmployeeOut])
def list_employees(db: Session = Depends(get_db), _: AuthIdentity = Depends(require_operator)) -> list[EmployeeOut]:
    rows = db.scalars(select(Employee).where(Employee.is_active.is_(True)).order_by(Employee.name)).all()
    return [employee_out(row) for row in rows]


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    _: AuthIdentity = Depends(require_operator),
) -> EmployeeOut:
    employee = db.scalar(select(Employee).where(Employee.employee_id == employee_id, Employee.is_active.is_(True)))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee_out(employee)


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    user: AuthIdentity = Depends(require_operator),
) -> dict:
    employee = db.scalar(select(Employee).where(Employee.employee_id == employee_id, Employee.is_active.is_(True)))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee.is_active = False
    db.commit()
    return {"deleted": True, "employee_id": employee_id, "by": user.username}
