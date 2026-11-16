# FaceGuard Edge Mobile

React Native Android/iOS prototype for the NHAI offline facial recognition and liveness hackathon.

## Why this exists

The web dashboard in the root repository is useful for admin demos, but the hackathon requires a mobile, fully offline, React Native prototype. This app is the judge-facing mobile deliverable.

## Offline architecture

- Camera: `react-native-vision-camera`.
- On-device inference: `react-native-fast-tflite` with packaged `.tflite` assets.
- Face recognition: quantized MobileFaceNet/ArcFace-style embedding model.
- Liveness: active challenge-response checks across a short frame sequence.
- Local storage: encrypted employee gallery plus attendance queue.
- Sync: AWS/Datalake endpoint is contacted only after connectivity returns; synced queue rows are purged after server acknowledgement.

## Model files

Place these files in `mobile/assets/models/` before device builds:

```text
face_detector_int8.tflite
face_embedder_int8.tflite
face_landmarks_int8.tflite
```

Recommended model budget:

| Model | Target |
| --- | ---: |
| Face detector | 1-3 MB |
| Face embedder | 4-8 MB |
| Landmark/liveness helper | 1-4 MB |
| Total | < 15 MB |

The code includes a deterministic mock inference path for simulator demos. Device builds should enable the TFLite path by providing the model assets above.

## Commands

```bash
cd mobile
npm install
npm run android
npm run ios
```

If native `android/` and `ios/` folders are not present in the submitted zip, generate them with the React Native CLI before installing native pods:

```bash
npx react-native init FaceGuardEdge --version 0.75.4
cp -R src App.tsx app.json index.js assets package.json tsconfig.json babel.config.js metro.config.js jest.config.js FaceGuardEdge/
```

The code is intentionally kept in plain React Native TypeScript so it can be copied into an existing Datalake 3.0 React Native app without forcing a new app shell.

## Demo script

1. Disable network.
2. Enroll a field employee with name and employee ID.
3. Complete blink, head-turn, and smile liveness challenges.
4. Authenticate the same person offline in under one second.
5. Show the local pending sync count.
6. Re-enable network and press Sync.
7. Confirm server acknowledgement and local purge of synced attendance events.
