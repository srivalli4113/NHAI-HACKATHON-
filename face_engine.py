from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np


@dataclass(frozen=True)
class FaceBox:
    x: int
    y: int
    w: int
    h: int
    confidence: float


@dataclass(frozen=True)
class FaceEmbedding:
    box: FaceBox
    vector: np.ndarray
    latency_ms: float


class OfflineFaceEngine:
    def __init__(self, model_dir: str | Path, min_face_size: int = 64) -> None:
        self.model_dir = Path(model_dir)
        self.min_face_size = min_face_size
        cascade_names = [
            "haarcascade_frontalface_default.xml",
            "haarcascade_frontalface_alt2.xml",
            "haarcascade_frontalface_alt.xml",
            "haarcascade_profileface.xml",
        ]
        self.detectors = [
            cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / name))
            for name in cascade_names
            if (Path(cv2.data.haarcascades) / name).exists()
        ]
        self.session = self._load_onnx_session()

    def _load_onnx_session(self):
        candidates = sorted(self.model_dir.glob("**/*.onnx")) if self.model_dir.exists() else []
        if not candidates:
            return None
        try:
            import onnxruntime as ort

            providers = ["CPUExecutionProvider"]
            return ort.InferenceSession(str(candidates[0]), providers=providers)
        except Exception:
            return None

    def decode_image(self, image_bytes: bytes) -> np.ndarray:
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Invalid image payload")
        return image

    def detect_faces(self, image: np.ndarray) -> list[FaceBox]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_eq = cv2.equalizeHist(gray)
        candidates: list[FaceBox] = []
        attempts = [
            (gray, 1.08, 5, self.min_face_size),
            (gray_eq, 1.06, 4, max(40, self.min_face_size - 16)),
            (gray_eq, 1.04, 3, max(36, self.min_face_size - 24)),
        ]
        for detector in self.detectors:
            if detector.empty():
                continue
            for frame, scale, neighbors, min_size in attempts:
                faces = detector.detectMultiScale(
                    frame,
                    scaleFactor=scale,
                    minNeighbors=neighbors,
                    minSize=(min_size, min_size),
                )
                for x, y, w, h in faces:
                    candidates.append(FaceBox(int(x), int(y), int(w), int(h), 0.92))
        boxes = self._dedupe_boxes(candidates)
        boxes.sort(key=lambda b: b.w * b.h, reverse=True)
        return boxes

    def _dedupe_boxes(self, boxes: list[FaceBox]) -> list[FaceBox]:
        kept: list[FaceBox] = []
        for box in sorted(boxes, key=lambda b: b.w * b.h, reverse=True):
            if all(self._iou(box, other) < 0.35 for other in kept):
                kept.append(box)
        return kept

    def _iou(self, a: FaceBox, b: FaceBox) -> float:
        x1 = max(a.x, b.x)
        y1 = max(a.y, b.y)
        x2 = min(a.x + a.w, b.x + b.w)
        y2 = min(a.y + a.h, b.y + b.h)
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        union = a.w * a.h + b.w * b.h - inter
        return inter / union if union else 0.0

    def validate_quality(self, image: np.ndarray, box: FaceBox) -> tuple[bool, list[str]]:
        issues: list[str] = []
        h, w = image.shape[:2]
        if box.w < self.min_face_size or box.h < self.min_face_size:
            issues.append("Face is too small")
        if box.x < 0 or box.y < 0 or box.x + box.w > w or box.y + box.h > h:
            issues.append("Face is outside frame")
        crop = image[box.y : box.y + box.h, box.x : box.x + box.w]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = float(gray.mean())
        if blur < 55:
            issues.append("Image is blurry")
        if brightness < 45:
            issues.append("Image is too dark")
        if brightness > 220:
            issues.append("Image is overexposed")
        return not issues, issues

    def embed_faces(self, image: np.ndarray) -> list[FaceEmbedding]:
        start = perf_counter()
        boxes = self.detect_faces(image)
        embeddings: list[FaceEmbedding] = []
        for box in boxes:
            crop = image[box.y : box.y + box.h, box.x : box.x + box.w]
            vector = self._embed_crop(crop)
            latency = (perf_counter() - start) * 1000
            embeddings.append(FaceEmbedding(box=box, vector=vector, latency_ms=latency))
        return embeddings

    def _embed_crop(self, crop: np.ndarray) -> np.ndarray:
        if self.session is not None:
            return self._onnx_embedding(crop)
        return self._opencv_embedding(crop)

    def _onnx_embedding(self, crop: np.ndarray) -> np.ndarray:
        resized = cv2.resize(crop, (112, 112))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32)
        tensor = ((rgb - 127.5) / 127.5).transpose(2, 0, 1)[None, :, :, :]
        input_name = self.session.get_inputs()[0].name
        output = self.session.run(None, {input_name: tensor})[0][0].astype(np.float32)
        return self._normalize(output)

    def _opencv_embedding(self, crop: np.ndarray) -> np.ndarray:
        resized = cv2.resize(crop, (96, 96))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        hist = cv2.calcHist([gray], [0], None, [128], [0, 256]).flatten()
        edges = cv2.Canny(gray, 60, 140)
        edge_hist = cv2.resize(edges, (16, 16)).flatten().astype(np.float32) / 255.0
        moments = cv2.HuMoments(cv2.moments(gray)).flatten().astype(np.float32)
        vector = np.concatenate([hist.astype(np.float32), edge_hist, moments])
        return self._normalize(vector)

    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector.astype(np.float32)
        return (vector / norm).astype(np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return float(np.dot(a, b) / (a_norm * b_norm))

