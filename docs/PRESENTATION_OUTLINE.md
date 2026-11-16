# Hackathon Presentation Outline

## 1. Problem

NHAI field deployments need identity verification that remains reliable in zero-network environments and resists spoofing attacks.

## 2. Solution

FaceGuard Edge: a React Native Android/iOS offline facial recognition and active liveness app with local encrypted storage, attendance queueing, and Datalake 3.0 sync/purge after connectivity returns.

## 3. Architecture

- React Native mobile app.
- VisionCamera frame capture.
- INT8 TFLite face detector, embedder, and landmark helper.
- Encrypted local employee gallery and attendance queue.
- Active liveness: blink, head turn, smile, texture, exposure checks.
- AWS/Datalake sync with purge after acknowledgement.

## 4. Differentiators

- Entire identity decision happens on device.
- Model budget below 20 MB using INT8 mobile models.
- Active liveness avoids dependence on a large anti-spoof network.
- Sync queue survives zero-network zones and purges after server acknowledgement.
- Existing FastAPI dashboard remains available as an admin/reference demo.

## 5. Demo Flow

1. Disable network on the phone.
2. Enroll field personnel in the React Native app.
3. Complete blink, head-turn, and smile challenge.
4. Authenticate the user offline in under one second.
5. Show attendance queued locally.
6. Re-enable network.
7. Sync queued event to AWS/Datalake mock endpoint.
8. Show local purge after acknowledgement.

## 6. Scaling Path

- Add production-trained Indian demographic model checkpoint.
- Add signed Datalake REST integration once endpoint details are available.
- Add remote policy updates for thresholds and challenge sequence.
- Add device health monitoring and model drift reports.


## 7. Latest Demo Enhancements

- React Native Enroll, Recognize, and Sync flows added for the mandatory mobile deliverable.
- Active liveness challenge covers blink, left turn, right turn, smile, texture, and exposure checks.
- Model manifest budgets detector, embedder, and landmark models at 15 MB total.
- Encrypted local gallery and attendance queue isolate biometric templates from network availability.
- Datalake sync purges acknowledged records and retains failed records for retry.
- Optional web/backend dashboard remains available for admin inspection and audit export.
