from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from ai.face_engine import FaceBox


@dataclass(frozen=True)
class LivenessResult:
    status: str
    score: float
    blink_score: float
    head_movement_score: float
    texture_score: float
    screen_attack_score: float
    replay_attack_score: float
    reasons: list[str]


class LivenessEngine:
    def __init__(self) -> None:
        self.face_mesh = None
        try:
            import mediapipe as mp

            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=4,
                refine_landmarks=True,
                min_detection_confidence=0.5,
            )
        except Exception:
            self.face_mesh = None

    def evaluate(self, image: np.ndarray, box: FaceBox | None = None) -> LivenessResult:
        crop = self._crop(image, box)
        blink_score = self._blink_score(crop)
        head_score = self._head_pose_score(crop)
        texture_score = self._texture_score(crop)
        screen_score = self._screen_attack_score(crop)
        replay_score = self._replay_attack_score(crop)
        score = float(
            np.clip(
                0.24 * blink_score
                + 0.20 * head_score
                + 0.26 * texture_score
                + 0.15 * (1 - screen_score)
                + 0.15 * (1 - replay_score),
                0,
                1,
            )
        )
        reasons = self._reasons(blink_score, head_score, texture_score, screen_score, replay_score)
        if score >= 0.68:
            status = "Live"
        elif score >= 0.45:
            status = "Suspicious"
        else:
            status = "Fake"
        return LivenessResult(
            status=status,
            score=round(score, 4),
            blink_score=round(blink_score, 4),
            head_movement_score=round(head_score, 4),
            texture_score=round(texture_score, 4),
            screen_attack_score=round(screen_score, 4),
            replay_attack_score=round(replay_score, 4),
            reasons=reasons,
        )

    def _crop(self, image: np.ndarray, box: FaceBox | None) -> np.ndarray:
        if box is None:
            return image
        return image[max(0, box.y) : box.y + box.h, max(0, box.x) : box.x + box.w]

    def _blink_score(self, crop: np.ndarray) -> float:
        if self.face_mesh is None:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            upper = gray[: max(1, gray.shape[0] // 2), :]
            return float(np.clip(cv2.Laplacian(upper, cv2.CV_64F).var() / 180.0, 0, 1))
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb)
        if not result.multi_face_landmarks:
            return 0.2
        landmarks = result.multi_face_landmarks[0].landmark
        left = self._eye_aspect_ratio(landmarks, [33, 160, 158, 133, 153, 144])
        right = self._eye_aspect_ratio(landmarks, [362, 385, 387, 263, 373, 380])
        ear = (left + right) / 2
        return float(np.clip(abs(ear - 0.18) / 0.14, 0.2, 1.0))

    def _eye_aspect_ratio(self, landmarks, idx: list[int]) -> float:
        pts = np.array([[landmarks[i].x, landmarks[i].y] for i in idx], dtype=np.float32)
        vertical = np.linalg.norm(pts[1] - pts[5]) + np.linalg.norm(pts[2] - pts[4])
        horizontal = 2.0 * np.linalg.norm(pts[0] - pts[3])
        return float(vertical / horizontal) if horizontal else 0.0

    def _head_pose_score(self, crop: np.ndarray) -> float:
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        left = gray[:, : gray.shape[1] // 2].mean()
        right = gray[:, gray.shape[1] // 2 :].mean()
        asymmetry = abs(float(left - right)) / 40.0
        return float(np.clip(0.45 + asymmetry, 0, 1))

    def _texture_score(self, crop: np.ndarray) -> float:
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F).var()
        hist = cv2.calcHist([gray], [0], None, [64], [0, 256]).flatten()
        entropy = -np.sum((hist / (hist.sum() + 1e-9)) * np.log2(hist / (hist.sum() + 1e-9) + 1e-9))
        return float(np.clip((lap / 140.0) * 0.55 + (entropy / 6.0) * 0.45, 0, 1))

    def _screen_attack_score(self, crop: np.ndarray) -> float:
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1].mean() / 255.0
        value = hsv[:, :, 2].mean() / 255.0
        specular = np.mean(hsv[:, :, 2] > 245)
        return float(np.clip(0.45 * specular + 0.35 * max(0, value - 0.75) + 0.20 * max(0, saturation - 0.65), 0, 1))

    def _replay_attack_score(self, crop: np.ndarray) -> float:
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        banding = np.abs(np.diff(gray.astype(np.float32), axis=0)).mean() / 35.0
        moire = cv2.Sobel(gray, cv2.CV_64F, 1, 1, ksize=3).var() / 3000.0
        return float(np.clip(0.55 * banding + 0.45 * moire, 0, 1))

    def _reasons(self, blink: float, head: float, texture: float, screen: float, replay: float) -> list[str]:
        reasons: list[str] = []
        if blink < 0.35:
            reasons.append("Low blink/eye micro-motion evidence")
        if head < 0.35:
            reasons.append("Weak head pose variation")
        if texture < 0.42:
            reasons.append("Flat print-like facial texture")
        if screen > 0.45:
            reasons.append("Screen glare or saturation pattern detected")
        if replay > 0.55:
            reasons.append("Replay/banding artifacts detected")
        return reasons or ["Liveness checks passed"]

