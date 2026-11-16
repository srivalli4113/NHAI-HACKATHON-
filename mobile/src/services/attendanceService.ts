import {identifyOffline} from '../engine/faceEngine';
import {enqueueAttendance} from './localStore';

export async function authenticateAttendance(input: {
  frameId: string;
  livenessScore: number;
  deviceId: string;
  latitude?: number;
  longitude?: number;
}) {
  const match = await identifyOffline(input.frameId, input.livenessScore);
  if (match.status === 'matched' && match.employee) {
    await enqueueAttendance({
      employeeId: match.employee.employeeId,
      name: match.employee.name,
      confidence: match.confidence,
      livenessScore: input.livenessScore,
      deviceId: input.deviceId,
      latitude: input.latitude,
      longitude: input.longitude,
      capturedAt: new Date().toISOString(),
    });
  }
  return match;
}
