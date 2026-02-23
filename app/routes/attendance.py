from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.attendance import AttendanceCreate, AttendanceResponse, AttendanceSummary
from app.database import get_attendance_collection, get_employees_collection
from app.utils import serialize_attendance
from typing import List, Optional

router = APIRouter()


@router.get("/", response_model=List[AttendanceResponse], summary="Get all attendance records")
async def get_all_attendance(date: Optional[str] = Query(None, description="Filter by date YYYY-MM-DD")):
    """Retrieve all attendance records, optionally filtered by date."""
    collection = get_attendance_collection()
    query = {}
    if date:
        query["date"] = date
    records = await collection.find(query).sort("date", -1).to_list(5000)
    return [serialize_attendance(r) for r in records]


@router.get(
    "/employee/{employee_id}",
    response_model=List[AttendanceResponse],
    summary="Get attendance for an employee",
)
async def get_employee_attendance(
    employee_id: str,
    date: Optional[str] = Query(None, description="Filter by specific date YYYY-MM-DD"),
):
    """Retrieve attendance records for a specific employee, optionally filtered by date."""
    # Verify employee exists
    emp_collection = get_employees_collection()
    if not await emp_collection.find_one({"employee_id": employee_id}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found.",
        )

    att_collection = get_attendance_collection()
    query = {"employee_id": employee_id}
    if date:
        query["date"] = date

    records = await att_collection.find(query).sort("date", -1).to_list(1000)
    return [serialize_attendance(r) for r in records]


@router.get(
    "/summary/{employee_id}",
    response_model=AttendanceSummary,
    summary="Get attendance summary for an employee",
)
async def get_attendance_summary(employee_id: str):
    """Get total, present, and absent counts for an employee."""
    emp_collection = get_employees_collection()
    if not await emp_collection.find_one({"employee_id": employee_id}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found.",
        )

    att_collection = get_attendance_collection()
    total = await att_collection.count_documents({"employee_id": employee_id})
    present = await att_collection.count_documents({"employee_id": employee_id, "status": "Present"})
    absent = total - present

    return AttendanceSummary(
        employee_id=employee_id,
        total=total,
        present=present,
        absent=absent,
    )


@router.post(
    "/",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mark attendance",
)
async def mark_attendance(attendance: AttendanceCreate):
    """Mark or update attendance for an employee on a given date."""
    emp_collection = get_employees_collection()
    att_collection = get_attendance_collection()

    # Verify employee exists
    if not await emp_collection.find_one({"employee_id": attendance.employee_id}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{attendance.employee_id}' not found.",
        )

    # Upsert: update if exists, else insert
    existing = await att_collection.find_one(
        {"employee_id": attendance.employee_id, "date": attendance.date}
    )

    if existing:
        await att_collection.update_one(
            {"employee_id": attendance.employee_id, "date": attendance.date},
            {"$set": {"status": attendance.status}},
        )
        updated = await att_collection.find_one(
            {"employee_id": attendance.employee_id, "date": attendance.date}
        )
        return serialize_attendance(updated)

    att_dict = attendance.model_dump()
    result = await att_collection.insert_one(att_dict)
    created = await att_collection.find_one({"_id": result.inserted_id})
    return serialize_attendance(created)
