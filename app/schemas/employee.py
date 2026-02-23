from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., min_length=1, description="Unique employee identifier")
    full_name: str = Field(..., min_length=1, description="Full name of the employee")
    email: EmailStr = Field(..., description="Work email address")
    department: str = Field(..., min_length=1, description="Department name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "employee_id": "EMP001",
                "full_name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
            }
        }
    }


class EmployeeResponse(BaseModel):
    id: str
    employee_id: str
    full_name: str
    email: str
    department: str
