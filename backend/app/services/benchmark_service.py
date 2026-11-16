from statistics import mean, quantiles
from time import perf_counter

import cv2
import numpy as np

from app.services.face_service import face_service


def run_benchmark(samples: int = 20) -> dict:
    latencies: list[float] = []
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.ellipse(image, (320, 220), (80, 105), 0, 0, 360, (190, 170, 145), -1)
    cv2.circle(image, (292, 205), 8, (25, 25, 25), -1)
    cv2.circle(image, (348, 205), 8, (25, 25, 25), -1)
    cv2.ellipse(image, (320, 255), (35, 14), 0, 0, 180, (30, 30, 30), 2)
    for _ in range(samples):
        start = perf_counter()
        face_service.engine.embed_faces(image)
        latencies.append((perf_counter() - start) * 1000)
    p95 = quantiles(latencies, n=20)[-1] if len(latencies) > 1 else latencies[0]
    return {
        "samples": samples,
        "average_latency_ms": round(mean(latencies), 2),
        "p95_latency_ms": round(p95, 2),
        "memory_note": "CPU-only path keeps embeddings in SQLite and streams frames per request.",
        "device": "CPU",
    }

