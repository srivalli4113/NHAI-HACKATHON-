import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import DatalakeQueueItem


def enqueue_event(db: Session, event_type: str, payload: dict[str, Any]) -> DatalakeQueueItem:
    item = DatalakeQueueItem(event_type=event_type, payload_json=json.dumps(payload, default=str))
    db.add(item)
    return item


def pending_items(db: Session, limit: int = 250) -> list[DatalakeQueueItem]:
    return list(
        db.scalars(
            select(DatalakeQueueItem)
            .where(DatalakeQueueItem.status.in_(["pending", "failed"]))
            .order_by(DatalakeQueueItem.created_at)
            .limit(limit)
        ).all()
    )


def mark_synced(item: DatalakeQueueItem) -> None:
    item.status = "synced"
    item.updated_at = datetime.now(timezone.utc)
    item.last_error = None


def mark_failed(item: DatalakeQueueItem, error: str) -> None:
    item.status = "failed"
    item.attempts += 1
    item.last_error = error[:2000]
    item.updated_at = datetime.now(timezone.utc)

