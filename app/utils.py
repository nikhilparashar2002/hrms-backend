def serialize_employee(emp: dict) -> dict:
    """Convert a MongoDB employee document to a serializable dict."""
    return {
        "id": str(emp["_id"]),
        "employee_id": emp["employee_id"],
        "full_name": emp["full_name"],
        "email": emp["email"],
        "department": emp["department"],
    }


def serialize_attendance(att: dict) -> dict:
    """Convert a MongoDB attendance document to a serializable dict."""
    return {
        "id": str(att["_id"]),
        "employee_id": att["employee_id"],
        "date": att["date"],
        "status": att["status"],
    }
