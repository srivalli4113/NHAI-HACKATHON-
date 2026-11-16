import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "offline"


def test_built_frontend_is_served_from_root():
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "<div id=\"root\"></div>" in response.text
