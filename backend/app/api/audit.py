from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.contracts import AuditLogOut
from app.security.auth import AuthIdentity, require_operator
from app.services.audit_service import export_csv, export_xlsx, list_logs

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=list[AuditLogOut])
def logs(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: AuthIdentity = Depends(require_operator),
) -> list:
    return list_logs(db, limit=limit, offset=offset)


@router.get("/export.csv")
def csv_export(db: Session = Depends(get_db), _: AuthIdentity = Depends(require_operator)) -> Response:
    return Response(
        content=export_csv(db),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )


@router.get("/export.xlsx")
def xlsx_export(db: Session = Depends(get_db), _: AuthIdentity = Depends(require_operator)) -> Response:
    return Response(
        content=export_xlsx(db),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=audit_logs.xlsx"},
    )
