from fastapi import APIRouter

from app.api import audit, auth, benchmark, dashboard, datalake, employees, liveness, recognition

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(employees.router)
api_router.include_router(recognition.router)
api_router.include_router(liveness.router)
api_router.include_router(dashboard.router)
api_router.include_router(audit.router)
api_router.include_router(datalake.router)
api_router.include_router(benchmark.router)

