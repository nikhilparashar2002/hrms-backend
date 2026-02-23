from fastapi import APIRouter, HTTPException, status
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.database import get_employees_collection, get_attendance_collection
from app.utils import serialize_employee
from typing import List

router = APIRouter()


@router.get("/", response_model=List[EmployeeResponse], summary="Get all employees")
async def get_employees():
    """Retrieve a list of all employees."""
    collection = get_employees_collection()
    employees = await collection.find().sort("full_name", 1).to_list(1000)
    return [serialize_employee(e) for e in employees]


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
)
async def create_employee(employee: EmployeeCreate):
    """Add a new employee. Employee ID and email must be unique."""
    collection = get_employees_collection()

    # Check duplicate employee_id
    if await collection.find_one({"employee_id": employee.employee_id}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with ID '{employee.employee_id}' already exists.",
        )

    # Check duplicate email
    if await collection.find_one({"email": employee.email}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with email '{employee.email}' already exists.",
        )

    emp_dict = employee.model_dump()
    result = await collection.insert_one(emp_dict)
    created = await collection.find_one({"_id": result.inserted_id})
    return serialize_employee(created)


@router.get("/{employee_id}", response_model=EmployeeResponse, summary="Get employee by ID")
async def get_employee(employee_id: str):
    """Retrieve a single employee by their employee ID."""
    collection = get_employees_collection()
    employee = await collection.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found.",
        )
    return serialize_employee(employee)


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an employee",
)
async def delete_employee(employee_id: str):
    """Delete an employee and all their attendance records."""
    emp_collection = get_employees_collection()
    att_collection = get_attendance_collection()

    result = await emp_collection.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found.",
        )

    # Cascade delete attendance records
    await att_collection.delete_many({"employee_id": employee_id})
