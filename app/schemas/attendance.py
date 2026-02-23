from pydantic import BaseModel, Field, field_validator
from enum import Enum
import re


class AttendanceStatus(str, Enum):
    present = "Present"
    absent = "Absent"


class AttendanceCreate(BaseModel):
    employee_id: str = Field(..., min_length=1)
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    status: AttendanceStatus

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "employee_id": "EMP001",
                "date": "2026-02-23",
                "status": "Present",
            }
        }
    }


class AttendanceResponse(BaseModel):
    id: str
    employee_id: str
    date: str
    status: str


class AttendanceSummary(BaseModel):
    employee_id: str
    total: int
    present: int
    absent: int
