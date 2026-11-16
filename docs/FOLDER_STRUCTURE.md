# Folder Structure

```text
backend/
  app/
    api/              FastAPI route modules
    core/             Settings and app configuration
    db/               SQLAlchemy engine and schema initialization
    integrations/     Datalake 3.0 queue and sync adapters
    models/           Database entities
    schemas/          Pydantic contracts
    security/         Auth, sessions, encryption
    services/         Business logic and AI orchestration
frontend/
  src/
    main.jsx          React operator console
    styles.css        Tailwind and layout styling
mobile/
  App.tsx             React Native judge-facing app shell
  src/
    engine/           Model manifest, matcher, and liveness evaluator
    screens/          Enrollment, recognition, and sync flows
    services/         Encrypted gallery, attendance queue, sync, purge
  assets/models/      Packaged INT8 TFLite models for mobile builds
ai/
  face_engine.py      Offline face detection and embeddings
  liveness.py         Anti-spoofing and liveness scoring
  models/             Local ONNX model mount point
docker/
  backend.Dockerfile
  frontend.Dockerfile
docs/
  ARCHITECTURE.md
  API.md
  DATALAKE_RN_INTEGRATION.md
  DEPLOYMENT.md
  MOBILE_PROTOTYPE.md
  PERFORMANCE.md
  PRESENTATION_OUTLINE.md
  SYSTEM_DESIGN.md
  TESTING_STRATEGY.md
tests/
  Backend smoke and security tests
```
