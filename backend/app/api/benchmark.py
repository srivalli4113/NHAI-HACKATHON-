from fastapi import APIRouter, Depends

from app.schemas.contracts import BenchmarkResult
from app.security.auth import AuthIdentity, require_operator
from app.services.benchmark_service import run_benchmark

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.post("/run", response_model=BenchmarkResult)
def benchmark(samples: int = 20, _: AuthIdentity = Depends(require_operator)) -> dict:
    return run_benchmark(samples=max(1, min(samples, 200)))
