import {LivenessChallengeType, LivenessFrame, LivenessResult} from '../types/domain';

const REQUIRED_CHALLENGES: LivenessChallengeType[] = ['blink', 'turn_left', 'turn_right', 'smile'];

export function evaluateLiveness(frames: LivenessFrame[]): LivenessResult {
  if (frames.length < 6) {
    return {
      passed: false,
      score: 0,
      completed: [],
      failed: REQUIRED_CHALLENGES,
      reasons: ['Need at least six frames for active liveness'],
    };
  }

  const completed = REQUIRED_CHALLENGES.filter(challenge => didComplete(challenge, frames));
  const failed = REQUIRED_CHALLENGES.filter(challenge => !completed.includes(challenge));
  const textureQuality = frames.filter(frame => frame.landmarks.sharpness >= 0.45).length / frames.length;
  const exposureQuality = frames.filter(frame => frame.landmarks.exposure >= 0.25 && frame.landmarks.exposure <= 0.82).length / frames.length;
  const challengeScore = completed.length / REQUIRED_CHALLENGES.length;
  const score = round(0.7 * challengeScore + 0.15 * textureQuality + 0.15 * exposureQuality);

  const reasons = [
    failed.includes('blink') ? 'Blink challenge not observed' : '',
    failed.includes('turn_left') ? 'Left head turn not observed' : '',
    failed.includes('turn_right') ? 'Right head turn not observed' : '',
    failed.includes('smile') ? 'Smile challenge not observed' : '',
    textureQuality < 0.6 ? 'Face texture is too flat or blurry' : '',
    exposureQuality < 0.6 ? 'Lighting is outside acceptable range' : '',
  ].filter(Boolean);

  return {
    passed: score >= 0.72 && completed.length >= 3,
    score,
    completed,
    failed,
    reasons: reasons.length ? reasons : ['Active liveness checks passed'],
  };
}

function didComplete(challenge: LivenessChallengeType, frames: LivenessFrame[]): boolean {
  switch (challenge) {
    case 'blink':
      return hasOpenClosedOpenEyeSequence(frames);
    case 'turn_left':
      return frames.some(frame => frame.landmarks.yaw <= -0.22);
    case 'turn_right':
      return frames.some(frame => frame.landmarks.yaw >= 0.22);
    case 'smile':
      return frames.some(frame => frame.landmarks.smile >= 0.62);
  }
}

function hasOpenClosedOpenEyeSequence(frames: LivenessFrame[]): boolean {
  const eye = frames.map(frame => (frame.landmarks.leftEyeOpen + frame.landmarks.rightEyeOpen) / 2);
  const firstOpen = eye.findIndex(value => value >= 0.55);
  const closed = eye.findIndex((value, index) => index > firstOpen && value <= 0.28);
  const secondOpen = eye.findIndex((value, index) => index > closed && value >= 0.55);
  return firstOpen >= 0 && closed > firstOpen && secondOpen > closed;
}

function round(value: number): number {
  return Math.round(value * 1000) / 1000;
}
