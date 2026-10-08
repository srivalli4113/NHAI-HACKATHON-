from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NHAI Offline Face Recognition"
    app_env: str = "local"
    database_url: str = "sqlite:///./offline_face.db"
    storage_dir: Path = Path("./storage")
    model_dir: Path = Path("../ai/models")
    admin_username: str = "admin"
    admin_password: str = "admin123"
    app_secret_key: str = Field(default="change-me-offline-secret-key-32-bytes")
    session_minutes: int = 480
    recognition_threshold: float = 0.46
    unknown_threshold: float = 0.38
    min_face_size: int = 64
    datalake_rest_endpoint: str | None = None
    datalake_local_export: Path = Path("./storage/datalake_events.jsonl")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    (settings.storage_dir / "photos").mkdir(parents=True, exist_ok=True)
    (settings.storage_dir / "exports").mkdir(parents=True, exist_ok=True)
    return settings

