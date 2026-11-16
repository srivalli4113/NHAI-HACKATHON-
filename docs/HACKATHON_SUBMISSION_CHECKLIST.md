# Hackathon Submission Checklist

## Mandatory Deliverables

- React Native Android/iOS prototype: `mobile/`.
- Offline facial recognition contract: `mobile/src/engine/faceEngine.ts`.
- Offline active liveness: `mobile/src/engine/livenessChallenge.ts`.
- Sync and purge mechanism: `mobile/src/services/syncService.ts`.
- Technical documentation: `docs/MOBILE_PROTOTYPE.md`, `docs/ARCHITECTURE.md`, `docs/PERFORMANCE.md`.
- Presentation outline: `docs/PRESENTATION_OUTLINE.md`.
- Optional admin/backend demo: `backend/` and `frontend/`.

## Before Final Build

- Add open-source INT8 TFLite model files to `mobile/assets/models/`.
- Include model licenses and training/evaluation notes.
- Run Android build on a 3 GB RAM mid-range device.
- Run iOS build on an iOS 12+ compatible simulator/device if available.
- Record benchmark table: average latency, p95 latency, model size, memory, false accept/reject sample results.
- Configure AWS/Datalake staging endpoint and token.
- Capture a 2-3 minute demo video with airplane mode enabled for enrollment/authentication.

## Judge Talking Points

- The app makes identity decisions locally; network is not in the inference loop.
- Active liveness gives strong spoof resistance without a large anti-spoof model.
- Encrypted local storage protects face templates and queued attendance.
- Queue-first sync prevents data loss in remote highway locations.
- Purge-after-acknowledgement reduces privacy risk on field devices.
