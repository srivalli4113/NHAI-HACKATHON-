export type LivenessChallengeType = 'blink' | 'turn_left' | 'turn_right' | 'smile';

export type FaceBox = {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
};

export type FaceLandmarks = {
  leftEyeOpen: number;
  rightEyeOpen: number;
  yaw: number;
  smile: number;
  sharpness: number;
  exposure: number;
};

export type FaceEmbedding = {
  box: FaceBox;
  vector: number[];
  landmarks: FaceLandmarks;
  latencyMs: number;
};

export type EmployeeProfile = {
  id: string;
  employeeId: string;
  name: string;
  department: string;
  designation: string;
  embedding: number[];
  createdAt: string;
  active: boolean;
};

export type RecognitionMatch = {
  employee: EmployeeProfile | null;
  confidence: number;
  distance: number;
  status: 'matched' | 'unknown' | 'spoof_blocked' | 'no_face';
  latencyMs: number;
};

export type LivenessFrame = {
  timestampMs: number;
  landmarks: FaceLandmarks;
};

export type LivenessResult = {
  passed: boolean;
  score: number;
  completed: LivenessChallengeType[];
  failed: LivenessChallengeType[];
  reasons: string[];
};

export type AttendanceEvent = {
  id: string;
  employeeId: string;
  name: string;
  confidence: number;
  livenessScore: number;
  deviceId: string;
  latitude?: number;
  longitude?: number;
  capturedAt: string;
  syncStatus: 'pending' | 'synced' | 'failed';
  attempts: number;
  lastError?: string;
};
