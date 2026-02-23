from fastapi import APIRouter
from app.database import get_employees_collection, get_attendance_collection
from datetime import date

router = APIRouter()


@router.get("/", summary="Dashboard summary stats")
async def get_dashboard():
    """
    Returns aggregated numbers for the dashboard:
    total employees, today present/absent/unmarked, and department breakdown.
    """
    emp_col = get_employees_collection()
    att_col = get_attendance_collection()

    today = date.today().isoformat()

    total_employees = await emp_col.count_documents({})
    present_today = await att_col.count_documents({"date": today, "status": "Present"})
    absent_today = await att_col.count_documents({"date": today, "status": "Absent"})
    marked_today = present_today + absent_today
    not_marked_today = max(0, total_employees - marked_today)

    # department breakdown
    pipeline = [
        {"$group": {"_id": "$department", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    dept_cursor = emp_col.aggregate(pipeline)
    departments = [
        {"department": doc["_id"], "count": doc["count"]}
        async for doc in dept_cursor
    ]

    return {
        "total_employees": total_employees,
        "present_today": present_today,
        "absent_today": absent_today,
        "not_marked_today": not_marked_today,
        "departments": departments,
        "today": today,
    }
