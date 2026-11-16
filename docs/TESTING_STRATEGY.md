# Testing Strategy

## Unit Tests

- Database schema creation.
- Password hashing and session token lifecycle.
- Embedding encryption/decryption.
- Audit log export.
- Datalake local queue sync.
- Liveness scoring contract.
- Mobile active liveness challenge pass/fail sequences.
- Mobile model footprint manifest under 20 MB.

## Integration Tests

- Register employee with valid face image.
- Reject duplicate employee ID.
- Reject no-face registration image.
- Recognition returns known/unknown results.
- Attendance persistence creates attendance and audit rows.
- CSV/XLSX export returns correct headers.
- React Native enrollment creates encrypted local employee templates.
- React Native attendance queues only after liveness and identity pass.
- React Native sync purges acknowledged events and retains failed events.

## Field Tests

- Indoor bright light, indoor low light, toll plaza booth lighting.
- Multiple faces in frame.
- Printed photo attack.
- Mobile screen attack at different brightness levels.
- Replay video attack.
- Network disconnected for full mobile enrollment, recognition, liveness, attendance queue, and later sync flow.

## Acceptance Targets

- Recognition plus liveness latency: under 1 second on a standard mid-range mobile device.
- Mobile packaged model footprint: under 20 MB.
- Supported device floor: Android 8.0+ and iOS 12+ with 3 GB RAM.
- False accept rate: tuned using local threshold validation set.
- Liveness spoof detection: active challenge-response plus landmark/quality checks with all spoof attempts audit logged.
- Zero internet calls during inference.
