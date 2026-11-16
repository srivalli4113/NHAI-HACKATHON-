from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.integrations.datalake import LocalSyncAdapter, RestSyncAdapter
from app.models.entities import DatalakeQueueItem
from app.security.auth import AuthIdentity, require_operator

router = APIRouter(prefix="/datalake", tags=["datalake"])


@router.get("/queue")
def queue(db: Session = Depends(get_db), _: AuthIdentity = Depends(require_operator)) -> list[dict]:
    rows = db.scalars(select(DatalakeQueueItem).order_by(desc(DatalakeQueueItem.created_at)).limit(200)).all()
    return [
        {
            "id": row.id,
            "event_type": row.event_type,
            "status": row.status,
            "attempts": row.attempts,
            "created_at": row.created_at,
            "last_error": row.last_error,
        }
        for row in rows
    ]


@router.post("/sync/local")
def sync_local(db: Session = Depends(get_db), _: AuthIdentity = Depends(require_operator)) -> dict:
    return LocalSyncAdapter().sync(db)


@router.post("/sync/rest")
def sync_rest(db: Session = Depends(get_db), _: AuthIdentity = Depends(require_operator)) -> dict:
    return RestSyncAdapter().sync(db)
