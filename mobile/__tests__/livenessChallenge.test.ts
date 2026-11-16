import {evaluateLiveness} from '../src/engine/livenessChallenge';
import {LivenessFrame} from '../src/types/domain';

function frame(timestampMs: number, eyeOpen: number, yaw: number, smile: number): LivenessFrame {
  return {
    timestampMs,
    landmarks: {
      leftEyeOpen: eyeOpen,
      rightEyeOpen: eyeOpen,
      yaw,
      smile,
      sharpness: 0.76,
      exposure: 0.52,
    },
  };
}

test('passes active liveness when blink, turns, and smile are present', () => {
  const result = evaluateLiveness([
    frame(0, 0.74, 0.01, 0.3),
    frame(150, 0.18, 0.01, 0.3),
    frame(300, 0.76, 0.01, 0.3),
    frame(450, 0.72, -0.31, 0.32),
    frame(600, 0.72, 0.32, 0.32),
    frame(750, 0.72, 0.01, 0.76),
  ]);

  expect(result.passed).toBe(true);
  expect(result.score).toBeGreaterThanOrEqual(0.72);
});

test('rejects static photo-like frames', () => {
  const result = evaluateLiveness([
    frame(0, 0.72, 0.01, 0.3),
    frame(150, 0.72, 0.01, 0.3),
    frame(300, 0.72, 0.01, 0.3),
    frame(450, 0.72, 0.01, 0.3),
    frame(600, 0.72, 0.01, 0.3),
    frame(750, 0.72, 0.01, 0.3),
  ]);

  expect(result.passed).toBe(false);
  expect(result.failed).toContain('blink');
});
