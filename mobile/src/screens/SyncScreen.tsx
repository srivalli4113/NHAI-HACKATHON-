import React, {useEffect, useState} from 'react';
import {Pressable, StyleSheet, Text, TextInput, View} from 'react-native';
import {loadAttendanceQueue} from '../services/localStore';
import {syncWithDatalake, SyncSummary} from '../services/syncService';
import {StatusPill} from '../components/StatusPill';

export function SyncScreen() {
  const [endpoint, setEndpoint] = useState('https://datalake.example.gov.in/api/attendance');
  const [pending, setPending] = useState(0);
  const [summary, setSummary] = useState<SyncSummary | null>(null);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    const queue = await loadAttendanceQueue();
    setPending(queue.length);
  }

  useEffect(() => {
    refresh();
  }, []);

  async function sync() {
    setBusy(true);
    try {
      const result = await syncWithDatalake(endpoint, 'replace-with-datalake-token');
      setSummary(result);
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Sync and Purge</Text>
      <Text style={styles.copy}>Attendance events remain local until connectivity returns and Datalake acknowledges receipt.</Text>

      <View style={styles.result}>
        <StatusPill label={`${pending} pending`} tone={pending ? 'warn' : 'good'} />
        <Text style={styles.resultText}>Synced events are removed from encrypted local storage.</Text>
      </View>

      <TextInput style={styles.input} value={endpoint} onChangeText={setEndpoint} autoCapitalize="none" />
      <Pressable style={styles.primaryButton} onPress={sync} disabled={busy}>
        <Text style={styles.primaryText}>{busy ? 'Syncing...' : 'Sync When Online'}</Text>
      </Pressable>

      {summary ? (
        <View style={styles.result}>
          <StatusPill label={summary.online ? 'online' : 'offline'} tone={summary.online ? 'good' : 'warn'} />
          <Text style={styles.resultText}>{summary.message}</Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {gap: 12},
  title: {fontSize: 24, fontWeight: '800', color: '#101828'},
  copy: {fontSize: 14, lineHeight: 20, color: '#475467'},
  input: {
    borderColor: '#CBD5E1',
    borderRadius: 8,
    borderWidth: 1,
    color: '#101828',
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
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
