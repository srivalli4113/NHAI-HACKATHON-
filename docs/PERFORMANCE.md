# Performance Optimization Strategy

## Runtime

- Mobile-first path uses packaged INT8 TFLite models through `react-native-fast-tflite`.
- Target per-authentication budget: detector 80-150 ms, landmark/liveness frames 250-450 ms, embedder 60-120 ms, local matching under 30 ms for a small field gallery.
- Use NNAPI on Android and Core ML acceleration where available, with CPU fallback for Android 8.0+ and iOS 12+.
- Keep the total packaged model footprint below 20 MB; the current manifest budgets 15 MB.
- Optional backend demo uses CPU-only ONNX Runtime provider by default for maximum edge compatibility.
- Cache active employee embeddings in service memory when gallery size grows beyond demo scale.
- Resize frames before detection for real-time recognition, then crop original frame for embedding.
- Store normalized float32 embeddings to reduce compute during cosine comparison.
- Keep audit and attendance inserts batched per frame.

## Model Strategy

- Use quantized MobileFaceNet/ArcFace mobile TFLite for the final mobile demo.
- Use local InsightFace ONNX model for the optional backend/admin demo.
- Keep OpenCV fallback for hardware smoke tests and no-model validation.
- Quantize ONNX model to INT8 after accuracy validation.
- Benchmark thresholds on the final mobile camera, lighting, and target CPU.

## Mobile Benchmark Targets

| Metric | Target |
| --- | ---: |
| App model footprint | <= 20 MB |
| Recognition + liveness | < 1 second |
| RAM on device | <= 3 GB supported |
| OS support | Android 8.0+, iOS 12+ |
| Recognition accuracy | > 95% on final calibrated gallery |
| Offline cloud calls | 0 during enrollment and authentication |

## Benchmarking

Use:

```bash
curl -X POST "http://localhost:8000/api/benchmark/run?samples=50" \
  -H "Authorization: Bearer <token>"
```

Track:

- Average latency.
- P95 latency.
- Face detection rate.
- CPU load.
- Memory usage.
- Database size and embedding gallery size.
