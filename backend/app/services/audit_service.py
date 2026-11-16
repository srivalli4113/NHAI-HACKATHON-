from __future__ import annotations

import csv
from io import BytesIO, StringIO

from openpyxl import Workbook
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.entities import AuditLog


def log_event(
    db: Session,
    user: str,
    event_type: str,
    confidence: float | None,
    liveness_score: float | None,
    result: str,
    details: str | None = None,
) -> AuditLog:
    row = AuditLog(
        user=user,
        event_type=event_type,
        confidence=confidence,
        liveness_score=liveness_score,
        result=result,
        details=details,
    )
    db.add(row)
    return row


def list_logs(db: Session, limit: int = 100, offset: int = 0) -> list[AuditLog]:
    return list(db.scalars(select(AuditLog).order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit)).all())


def export_csv(db: Session) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "User", "Event Type", "Confidence", "Liveness Score", "Result", "Details"])
    for row in db.scalars(select(AuditLog).order_by(desc(AuditLog.timestamp))).all():
        writer.writerow([row.timestamp, row.user, row.event_type, row.confidence, row.liveness_score, row.result, row.details])
    return output.getvalue()


def export_xlsx(db: Session) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Audit Logs"
    sheet.append(["Timestamp", "User", "Event Type", "Confidence", "Liveness Score", "Result", "Details"])
    for row in db.scalars(select(AuditLog).order_by(desc(AuditLog.timestamp))).all():
        sheet.append([str(row.timestamp), row.user, row.event_type, row.confidence, row.liveness_score, row.result, row.details])
    stream = BytesIO()
    workbook.save(stream)
    return stream.getvalue()

