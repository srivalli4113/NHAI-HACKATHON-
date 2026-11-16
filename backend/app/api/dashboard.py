from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.contracts import DashboardMetrics
from app.security.auth import AuthIdentity, require_operator
from app.services.dashboard_service import dashboard_metrics

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
def metrics(db: Session = Depends(get_db), _: AuthIdentity = Depends(require_operator)) -> dict:
    return dashboard_metrics(db)
