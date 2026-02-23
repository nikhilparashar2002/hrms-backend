from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from app.database import connect_db, close_db, ensure_indexes
from app.routes import employees, attendance, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown using the modern lifespan API."""
    await connect_db()
    await ensure_indexes()
    yield
    await close_db()


app = FastAPI(
    title="HRMS Lite API",
    description="A lightweight Human Resource Management System backend built with FastAPI and MongoDB.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
import os
_frontend = os.getenv("FRONTEND_URL", "")
_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]
if _frontend:
    _origins.append(_frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ── Global exception handler ─────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Turn Pydantic's verbose validation errors into something readable."""
    errors = []
    for e in exc.errors():
        field = " → ".join(str(loc) for loc in e["loc"] if loc != "body")
        errors.append(f"{field}: {e['msg']}" if field else e["msg"])
    return JSONResponse(
        status_code=422,
        content={"detail": errors if len(errors) > 1 else errors[0]},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "HRMS Lite API is running 🚀"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
