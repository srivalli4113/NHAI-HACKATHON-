# Datalake 3.0 React Native Integration Guide

## Integration Points

The mobile prototype is organized so the Datalake 3.0 app can adopt it module by module:

| Need | File |
| --- | --- |
| Face template creation | `mobile/src/services/enrollmentService.ts` |
| Offline identity match | `mobile/src/engine/faceEngine.ts` |
| Liveness decision | `mobile/src/engine/livenessChallenge.ts` |
| Attendance queue | `mobile/src/services/attendanceService.ts` |
| AWS/Datalake sync and purge | `mobile/src/services/syncService.ts` |
| Encrypted local storage | `mobile/src/services/localStore.ts` |

## App Permissions

Android:

- `android.permission.CAMERA`
- `android.permission.ACCESS_FINE_LOCATION` if geo-tagging attendance
- `android.permission.ACCESS_NETWORK_STATE`
- `android.permission.INTERNET` for sync only

iOS:

- `NSCameraUsageDescription`
- `NSLocationWhenInUseUsageDescription` if geo-tagging attendance

## Production Wiring

1. Replace the deterministic simulator path in `embedFrame` with TFLite detector, embedder, and landmark model calls.
2. Store face templates with `react-native-encrypted-storage` or the Datalake app's existing secure storage layer.
3. Call `authenticateAttendance` from the attendance screen after camera permission is granted.
4. Call `syncWithDatalake` from the app's existing network-restored listener or manual sync action.
5. Keep the queue API idempotent by sending the stable `AttendanceEvent.id` to the server.

## Security Requirements

- Never send raw face images during offline authentication.
- Encrypt local embeddings and attendance events.
- Rotate device sync tokens through the existing Datalake session mechanism.
- Purge synced attendance rows after server acknowledgement.
- Keep an audit record of spoof-blocked attempts without storing biometric images unless policy explicitly allows it.

## Performance Requirements

- Run inference on resized frames.
- Keep gallery embeddings normalized to avoid repeated vector normalization.
- Benchmark on an Android 8+ device with 3 GB RAM.
- Calibrate match thresholds from a real enrolled sample set before field deployment.
