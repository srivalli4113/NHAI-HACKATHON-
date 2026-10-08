from fastapi import APIRouter, Depends

from app.schemas.contracts import BenchmarkResult
from app.security.auth import get_current_user
from app.services.benchmark_service import run_benchmark

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.post("/run", response_model=BenchmarkResult)
def benchmark(samples: int = 20, _: str = Depends(get_current_user)) -> dict:
    return run_benchmark(samples=max(1, min(samples, 200)))

