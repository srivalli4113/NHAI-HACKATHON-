from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import AttendanceLog, AuditLog, Employee


def dashboard_metrics(db: Session) -> dict:
    total_employees = db.scalar(select(func.count()).select_from(Employee).where(Employee.is_active.is_(True))) or 0
    recognition_count = db.scalar(select(func.count()).select_from(AttendanceLog).where(AttendanceLog.result == "recognized")) or 0
    failed_attempts = db.scalar(select(func.count()).select_from(AuditLog).where(AuditLog.result == "unknown")) or 0
    spoofing_attempts = db.scalar(select(func.count()).select_from(AuditLog).where(AuditLog.result == "spoofing_attempt")) or 0
    return {
        "total_employees": total_employees,
        "recognition_count": recognition_count,
        "failed_attempts": failed_attempts,
        "spoofing_attempts": spoofing_attempts,
        "daily_activity": _activity(db, days=7),
        "weekly_activity": _activity(db, days=28, bucket=7),
        "security_incidents": _security(db),
    }


def _activity(db: Session, days: int, bucket: int = 1) -> list[dict]:
    now = datetime.now(timezone.utc)
    rows = []
    for i in range(0, days, bucket):
        start = now - timedelta(days=i + bucket)
        end = now - timedelta(days=i)
        count = db.scalar(
            select(func.count()).select_from(AttendanceLog).where(AttendanceLog.timestamp >= start, AttendanceLog.timestamp < end)
        ) or 0
        rows.append({"label": start.strftime("%d %b"), "count": count})
    return list(reversed(rows))


def _security(db: Session) -> list[dict]:
    rows = []
    for result in ["unknown", "suspicious", "spoofing_attempt"]:
        count = db.scalar(select(func.count()).select_from(AuditLog).where(AuditLog.result == result)) or 0
        rows.append({"type": result, "count": count})
    return rows

