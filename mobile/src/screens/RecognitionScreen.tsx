import React, {useMemo, useState} from 'react';
import {Pressable, StyleSheet, Text, View} from 'react-native';
import {evaluateLiveness} from '../engine/livenessChallenge';
import {authenticateAttendance} from '../services/attendanceService';
import {LivenessFrame, RecognitionMatch} from '../types/domain';
import {StatusPill} from '../components/StatusPill';

export function RecognitionScreen() {
  const [match, setMatch] = useState<RecognitionMatch | null>(null);
  const [livenessScore, setLivenessScore] = useState(0);
  const [busy, setBusy] = useState(false);

  const frames = useMemo<LivenessFrame[]>(
    () => [
      frame(0, 0.74, 0.02, 0.32),
      frame(180, 0.18, 0.02, 0.31),
      frame(360, 0.76, 0.02, 0.35),
      frame(540, 0.72, -0.31, 0.34),
      frame(720, 0.72, 0.33, 0.36),
      frame(900, 0.72, 0.01, 0.74),
    ],
    [],
  );

  async function recognize() {
    setBusy(true);
    try {
      const liveness = evaluateLiveness(frames);
      setLivenessScore(liveness.score);
      const result = await authenticateAttendance({
        frameId: 'NHAI-1024:Field Engineer Demo:front',
        livenessScore: liveness.score,
        deviceId: 'NHAI-RN-DEMO-01',
      });
      setMatch(result);
    } finally {
      setBusy(false);
    }
  }

  const tone = match?.status === 'matched' ? 'good' : match?.status === 'spoof_blocked' ? 'bad' : 'warn';

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Offline Authentication</Text>
      <Text style={styles.copy}>Blink, head-turn, and smile checks are evaluated before attendance is queued.</Text>

      <View style={styles.cameraMock}>
        <View style={styles.faceBox} />
        <Text style={styles.cameraText}>VisionCamera live preview</Text>
      </View>

      <Pressable style={styles.primaryButton} onPress={recognize} disabled={busy}>
        <Text style={styles.primaryText}>{busy ? 'Checking...' : 'Run Liveness + Identify'}</Text>
      </Pressable>

      {match ? (
        <View style={styles.result}>
          <StatusPill label={match.status.replace('_', ' ')} tone={tone} />
          <Text style={styles.resultText}>Confidence: {(match.confidence * 100).toFixed(1)}%</Text>
          <Text style={styles.resultText}>Liveness: {(livenessScore * 100).toFixed(1)}%</Text>
          <Text style={styles.resultText}>Latency: {match.latencyMs} ms</Text>
        </View>
      ) : null}
    </View>
  );
}

function frame(timestampMs: number, eyeOpen: number, yaw: number, smile: number): LivenessFrame {
  return {
    timestampMs,
    landmarks: {
      leftEyeOpen: eyeOpen,
      rightEyeOpen: eyeOpen,
      yaw,
      smile,
      sharpness: 0.74,
      exposure: 0.51,
    },
  };
}

const styles = StyleSheet.create({
  screen: {gap: 12},
  title: {fontSize: 24, fontWeight: '800', color: '#101828'},
  copy: {fontSize: 14, lineHeight: 20, color: '#475467'},
  cameraMock: {
    alignItems: 'center',
    aspectRatio: 0.82,
    backgroundColor: '#111827',
    borderRadius: 8,
    justifyContent: 'center',
    overflow: 'hidden',
  },
  faceBox: {
    borderColor: '#7DD3FC',
    borderRadius: 8,
    borderWidth: 3,
    height: 190,
    position: 'absolute',
    width: 160,
  },
  cameraText: {bottom: 18, color: '#E5E7EB', position: 'absolute'},
  primaryButton: {
    alignItems: 'center',
    backgroundColor: '#0B5FFF',
    borderRadius: 8,
    paddingVertical: 13,
  },
  primaryText: {color: '#FFFFFF', fontWeight: '800'},
  result: {
    borderColor: '#D0D5DD',
    borderRadius: 8,
    borderWidth: 1,
    gap: 8,
    padding: 12,
  },
  resultText: {color: '#344054'},
});
