import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app.db.session import SessionLocal
from app.main import app
from app.models.entities import AdminSession, UserAccount


def remove_test_account(username: str) -> None:
    db = SessionLocal()
    try:
        db.execute(delete(AdminSession).where(AdminSession.username == username))
        db.execute(delete(UserAccount).where(UserAccount.username == username))
        db.commit()
    finally:
        db.close()


def test_employee_signup_is_limited_to_registration_access() -> None:
    username = f"employee_{uuid4().hex[:12]}"
    try:
        with TestClient(app) as client:
            signup = client.post(
                "/api/auth/signup",
                json={
                    "display_name": "Demo Employee",
                    "username": username,
                    "password": "demo123",
                    "role": "employee",
                },
            )
            assert signup.status_code == 201
            payload = signup.json()
            assert payload["role"] == "employee"
            assert payload["display_name"] == "Demo Employee"

            headers = {"Authorization": f"Bearer {payload['access_token']}"}
            profile = client.get("/api/auth/me", headers=headers)
            assert profile.status_code == 200
            assert profile.json()["username"] == username

            protected = client.get("/api/dashboard/metrics", headers=headers)
            assert protected.status_code == 403
            assert client.get("/api/employees", headers=headers).status_code == 403
            assert client.get("/api/datalake/queue", headers=headers).status_code == 403
    finally:
        remove_test_account(username)


def test_operator_signup_can_open_the_full_dashboard() -> None:
    username = f"operator_{uuid4().hex[:12]}"
    try:
        with TestClient(app) as client:
            signup = client.post(
                "/api/auth/signup",
                json={
                    "display_name": "Demo Operator",
                    "username": username,
                    "password": "demo123",
                    "role": "operator",
                },
            )
            assert signup.status_code == 201
            headers = {"Authorization": f"Bearer {signup.json()['access_token']}"}

            dashboard = client.get("/api/dashboard/metrics", headers=headers)
            assert dashboard.status_code == 200
            assert "total_employees" in dashboard.json()
            assert client.get("/api/audit/logs", headers=headers).status_code == 200
            assert client.get("/api/datalake/queue", headers=headers).status_code == 200
    finally:
        remove_test_account(username)
