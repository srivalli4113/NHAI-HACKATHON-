import NetInfo from '@react-native-community/netinfo';
import {AttendanceEvent} from '../types/domain';
import {loadAttendanceQueue, replaceAttendanceQueue} from './localStore';

export type SyncSummary = {
  online: boolean;
  attempted: number;
  synced: number;
  failed: number;
  purged: number;
  message: string;
};

export async function syncWithDatalake(endpoint: string, token: string): Promise<SyncSummary> {
  const network = await NetInfo.fetch();
  const queue = await loadAttendanceQueue();
  const pending = queue.filter(event => event.syncStatus !== 'synced');

  if (!network.isConnected || pending.length === 0) {
    return {
      online: Boolean(network.isConnected),
      attempted: 0,
      synced: 0,
      failed: 0,
      purged: 0,
      message: pending.length === 0 ? 'No pending attendance events' : 'Device is offline',
    };
  }

  const syncedIds: string[] = [];
  const updated: AttendanceEvent[] = [];

  for (const event of queue) {
    if (event.syncStatus === 'synced') {
      syncedIds.push(event.id);
      continue;
    }

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'attendance',
          payload: event,
        }),
      });

      if (!response.ok) {
        throw new Error(`Datalake rejected event with ${response.status}`);
      }
      syncedIds.push(event.id);
    } catch (error) {
      updated.push({
        ...event,
        syncStatus: 'failed',
        attempts: event.attempts + 1,
        lastError: error instanceof Error ? error.message : 'Unknown sync error',
      });
    }
  }

  await replaceAttendanceQueue(updated);
  const purged = syncedIds.length;

  return {
    online: true,
    attempted: pending.length,
    synced: syncedIds.length,
    failed: updated.length,
    purged,
    message: `Synced ${syncedIds.length}, purged ${purged}, retained ${updated.length}`,
  };
}
