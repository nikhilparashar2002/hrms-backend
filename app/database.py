import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "hrms_lite")

client: AsyncIOMotorClient = None


async def connect_db():
    global client
    client = AsyncIOMotorClient(MONGODB_URL)


async def close_db():
    global client
    if client:
        client.close()


def get_database():
    return client[DATABASE_NAME]


def get_employees_collection():
    return client[DATABASE_NAME].get_collection("employees")


def get_attendance_collection():
    return client[DATABASE_NAME].get_collection("attendance")


async def ensure_indexes():
    """Create indexes so lookups don't do full collection scans."""
    db = client[DATABASE_NAME]

    # employees: unique on employee_id and email
    await db["employees"].create_index("employee_id", unique=True)
    await db["employees"].create_index("email", unique=True)

    # attendance: unique per employee+date combo; also index date alone for filtering
    await db["attendance"].create_index(
        [("employee_id", 1), ("date", 1)], unique=True
    )
    await db["attendance"].create_index("date")
