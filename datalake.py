from __future__ import annotations

import json
from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.integrations.queue import mark_failed, mark_synced, pending_items


class LocalSyncAdapter:
    def sync(self, db: Session, path: Path | None = None) -> dict:
        settings = get_settings()
        export_path = path or settings.datalake_local_export
        export_path.parent.mkdir(parents=True, exist_ok=True)
        items = pending_items(db)
        with export_path.open("a", encoding="utf-8") as handle:
            for item in items:
                handle.write(json.dumps({"id": item.id, "type": item.event_type, "payload": json.loads(item.payload_json)}) + "\n")
                mark_synced(item)
        db.commit()
        return {"synced": len(items), "path": str(export_path)}


class RestSyncAdapter:
    def sync(self, db: Session, endpoint: str | None = None) -> dict:
        settings = get_settings()
        target = endpoint or settings.datalake_rest_endpoint
        if not target:
            return {"synced": 0, "error": "Datalake REST endpoint is not configured"}
        synced = 0
        failed = 0
        with httpx.Client(timeout=5.0) as client:
            for item in pending_items(db):
                try:
                    response = client.post(target, json={"type": item.event_type, "payload": json.loads(item.payload_json)})
                    response.raise_for_status()
                    mark_synced(item)
                    synced += 1
                except Exception as exc:
                    mark_failed(item, str(exc))
                    failed += 1
        db.commit()
        return {"synced": synced, "failed": failed}

