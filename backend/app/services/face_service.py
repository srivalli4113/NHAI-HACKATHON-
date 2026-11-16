from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ai.face_engine import OfflineFaceEngine, cosine_similarity
from ai.liveness import LivenessEngine
from app.core.config import get_settings
from app.models.entities import AttendanceLog, Employee
from app.schemas.contracts import LivenessOut, RecognitionFace, RecognitionResponse
from app.security.crypto import decrypt_embedding, encrypt_embedding
from app.services.audit_service import log_event
from app.integrations.queue import enqueue_event


class FaceService:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.engine = OfflineFaceEngine(settings.model_dir, settings.min_face_size)
        self.liveness = LivenessEngine()

    async def read_image(self, upload: UploadFile) -> np.ndarray:
        data = await upload.read()
        try:
            return self.engine.decode_image(data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    async def register(
        self,
        db: Session,
        name: str,
        employee_id: str,
        department: str,
        designation: str,
        photograph: UploadFile,
        user: str,
    ) -> Employee:
        existing = db.scalar(select(Employee).where(Employee.employee_id == employee_id, Employee.is_active.is_(True)))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Employee ID already registered")
        image = await self.read_image(photograph)
        embeddings = self.engine.embed_faces(image)
        embedding = self._registration_embedding(embeddings)
        ok, issues = self.engine.validate_quality(image, embedding.box)
        if not ok:
            raise HTTPException(status_code=422, detail={"message": "Image quality validation failed", "issues": issues})
        duplicate = self._find_match(db, embedding.vector)
        if duplicate and duplicate[1] >= self.settings.recognition_threshold:
            raise HTTPException(status_code=409, detail=f"Duplicate face detected: {duplicate[0].employee_id}")
        photo_path = self._save_photo(employee_id, image)
        employee = Employee(
            employee_id=employee_id,
            name=name,
            department=department,
            designation=designation,
            embedding_encrypted=encrypt_embedding(embedding.vector),
            photo_path=str(photo_path),
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        log_event(db, user, "registration", 1.0, None, "success", f"Registered {employee_id}")
        enqueue_event(db, "employee_registered", {"employee_id": employee_id, "name": name, "department": department})
        return employee

    def _registration_embedding(self, embeddings):
        if not embeddings:
            raise HTTPException(status_code=400, detail="No face detected. Move closer, face the camera, and keep your full face visible.")
        if len(embeddings) == 1:
            return embeddings[0]
        ordered = sorted(embeddings, key=lambda item: item.box.w * item.box.h, reverse=True)
        largest_area = ordered[0].box.w * ordered[0].box.h
        competing = [item for item in ordered[1:] if item.box.w * item.box.h > largest_area * 0.55]
        if competing:
            raise HTTPException(status_code=400, detail=f"Multiple large faces detected ({len(competing) + 1}). Keep only one person in frame.")
        return ordered[0]

    def recognize(self, db: Session, image: np.ndarray, persist_attendance: bool, user: str) -> RecognitionResponse:
        started = perf_counter()
        embeddings = self._recognition_embeddings(self.engine.embed_faces(image))
        faces: list[RecognitionFace] = []
        for item in embeddings:
            match = self._find_match(db, item.vector)
            liveness = self.liveness.evaluate(image, item.box)
            employee, confidence = match if match else (None, 0.0)
            result = self._result(employee, confidence, liveness.score)
            now = datetime.now(timezone.utc)
            face = RecognitionFace(
                name=employee.name if employee else None,
                employee_id=employee.employee_id if employee else None,
                confidence=round(confidence, 4),
                timestamp=now,
                result=result,
                liveness=LivenessOut(**liveness.__dict__),
                box={"x": item.box.x, "y": item.box.y, "w": item.box.w, "h": item.box.h},
            )
            faces.append(face)
            log_event(db, user, "recognition", confidence, liveness.score, result, face.model_dump_json())
            enqueue_event(db, "recognition", face.model_dump(mode="json"))
            if persist_attendance:
                db.add(
                    AttendanceLog(
                        employee_pk=employee.id if employee else None,
                        employee_id=employee.employee_id if employee else None,
                        name=employee.name if employee else None,
                        confidence=confidence,
                        liveness_score=liveness.score,
                        result=result,
                    )
                )
        db.commit()
        return RecognitionResponse(latency_ms=round((perf_counter() - started) * 1000, 2), faces=faces)

    def _recognition_embeddings(self, embeddings):
        if len(embeddings) <= 1:
            return embeddings
        ordered = sorted(embeddings, key=lambda item: item.box.w * item.box.h, reverse=True)
        largest_area = ordered[0].box.w * ordered[0].box.h
        return [item for item in ordered if item.box.w * item.box.h >= largest_area * 0.55]

    def _result(self, employee: Employee | None, confidence: float, liveness_score: float) -> str:
        if liveness_score < 0.45:
            return "spoofing_attempt"
        if employee is None or confidence < self.settings.recognition_threshold:
            return "unknown"
        if liveness_score < 0.68:
            return "suspicious"
        return "recognized"

    def _find_match(self, db: Session, vector: np.ndarray) -> tuple[Employee, float] | None:
        employees = db.scalars(select(Employee).where(Employee.is_active.is_(True))).all()
        best: tuple[Employee, float] | None = None
        for employee in employees:
            stored = decrypt_embedding(employee.embedding_encrypted)
            score = cosine_similarity(vector, stored)
            if best is None or score > best[1]:
                best = (employee, score)
        if best is None or best[1] < self.settings.unknown_threshold:
            return None
        return best

    def _save_photo(self, employee_id: str, image: np.ndarray) -> Path:
        path = self.settings.storage_dir / "photos" / f"{employee_id}.jpg"
        cv2.imwrite(str(path), image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return path


face_service = FaceService()

