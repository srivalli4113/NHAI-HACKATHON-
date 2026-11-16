import {FaceEmbedding, RecognitionMatch} from '../types/domain';
import {cosineDistance, stableMockEmbedding} from './math';
import {loadEmployees} from '../services/localStore';

const MATCH_THRESHOLD = 0.38;

export async function embedFrame(frameId: string): Promise<FaceEmbedding> {
  const startedAt = Date.now();

  // Production builds replace this deterministic simulator path with
  // react-native-fast-tflite model calls for detector, embedder, and landmarks.
  const vector = stableMockEmbedding(frameId);
  const yawSeed = frameId.includes('left') ? -0.35 : frameId.includes('right') ? 0.35 : 0.02;
  const smileSeed = frameId.includes('smile') ? 0.78 : 0.34;
  const blinkSeed = frameId.includes('blink') ? 0.18 : 0.72;

  return {
    box: {x: 84, y: 128, width: 196, height: 196, confidence: 0.96},
    vector,
    landmarks: {
      leftEyeOpen: blinkSeed,
      rightEyeOpen: blinkSeed,
      yaw: yawSeed,
      smile: smileSeed,
      sharpness: 0.74,
      exposure: 0.52,
    },
    latencyMs: Date.now() - startedAt,
  };
}

export async function identifyOffline(frameId: string, livenessScore: number): Promise<RecognitionMatch> {
  const startedAt = Date.now();
  const embedding = await embedFrame(frameId);
  const employees = await loadEmployees();
  if (employees.length === 0) {
    return {
      employee: null,
      confidence: 0,
      distance: 1,
      status: 'unknown',
      latencyMs: Date.now() - startedAt,
    };
  }

  const ranked = employees
    .filter(employee => employee.active)
    .map(employee => ({
      employee,
      distance: cosineDistance(embedding.vector, employee.embedding),
    }))
    .sort((a, b) => a.distance - b.distance);

  const best = ranked[0];
  const confidence = Math.max(0, Math.min(1, 1 - best.distance / MATCH_THRESHOLD));
  const status = livenessScore < 0.72 ? 'spoof_blocked' : best.distance <= MATCH_THRESHOLD ? 'matched' : 'unknown';

  return {
    employee: status === 'matched' ? best.employee : null,
    confidence: round(confidence),
    distance: round(best.distance),
    status,
    latencyMs: Date.now() - startedAt,
  };
}

function round(value: number): number {
  return Math.round(value * 1000) / 1000;
}
