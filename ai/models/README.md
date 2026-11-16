# Local Model Directory

Place offline model artifacts here before deployment.

Recommended competition setup:

- InsightFace recognition ONNX model, for example a local `w600k_r50.onnx`.
- Keep files under this directory and mount it read-only in Docker.

Runtime behavior:

- The backend scans this directory for `.onnx` files.
- If a compatible ONNX model exists, ONNX Runtime CPU inference is used.
- If no ONNX model is present, the system uses a deterministic OpenCV fallback embedding so the full offline workflow remains functional for smoke tests.

No model is downloaded by the application at runtime.

