# Model Assets

Place quantized on-device models here before Android/iOS release builds.

Expected filenames:

- `face_detector_int8.tflite`
- `face_embedder_int8.tflite`
- `face_landmarks_int8.tflite`

The prototype keeps these files out of source control so evaluators can inspect code without large binary artifacts. Final submission builds should package the selected open-source model checkpoints and include their licenses.
