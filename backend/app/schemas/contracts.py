from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    display_name: str = Field(min_length=2, max_length=160)
    username: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=6, max_length=128)
    role: Literal["operator", "employee"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Literal["admin", "operator", "employee"]
    display_name: str


class AccountProfile(BaseModel):
    username: str
    display_name: str
    role: Literal["admin", "operator", "employee"]


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: str
    name: str
    department: str
    designation: str
    created_at: datetime
    is_active: bool


class RegistrationResponse(BaseModel):
    employee: EmployeeOut
    quality_passed: bool
    quality_issues: list[str]


class LivenessOut(BaseModel):
    status: str
    score: float
    blink_score: float
    head_movement_score: float
    texture_score: float
    screen_attack_score: float
    replay_attack_score: float
    reasons: list[str]


class RecognitionFace(BaseModel):
    name: str | None
    employee_id: str | None
    confidence: float
    timestamp: datetime
    result: str
    liveness: LivenessOut
    box: dict[str, int]


class RecognitionResponse(BaseModel):
    latency_ms: float
    faces: list[RecognitionFace]


class DashboardMetrics(BaseModel):
    total_employees: int
    recognition_count: int
    failed_attempts: int
    spoofing_attempts: int
    daily_activity: list[dict]
    weekly_activity: list[dict]
    security_incidents: list[dict]


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    user: str
    event_type: str
    confidence: float | None
    liveness_score: float | None
    result: str
    details: str | None


class BenchmarkResult(BaseModel):
    samples: int
    average_latency_ms: float
    p95_latency_ms: float
    memory_note: str
    device: str = Field(default="CPU")
