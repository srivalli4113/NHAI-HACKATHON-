export type ModelManifestEntry = {
  file: string;
  purpose: string;
  targetSizeMb: number;
  license: string;
};

export const modelManifest: ModelManifestEntry[] = [
  {
    file: 'face_detector_int8.tflite',
    purpose: 'Find and crop the largest face in the camera frame',
    targetSizeMb: 3,
    license: 'Open-source checkpoint required before release build',
  },
  {
    file: 'face_embedder_int8.tflite',
    purpose: 'Generate compact identity embedding for cosine matching',
    targetSizeMb: 8,
    license: 'Open-source checkpoint required before release build',
  },
  {
    file: 'face_landmarks_int8.tflite',
    purpose: 'Estimate eye openness, yaw, smile, exposure, and quality metrics',
    targetSizeMb: 4,
    license: 'Open-source checkpoint required before release build',
  },
];

export function totalModelBudgetMb(): number {
  return modelManifest.reduce((sum, model) => sum + model.targetSizeMb, 0);
}
